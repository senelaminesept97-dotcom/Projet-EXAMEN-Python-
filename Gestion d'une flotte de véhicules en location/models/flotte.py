"""
Classe Flotte : conteneur AGRÉGÉ de véhicules.

Relation d'AGRÉGATION : les véhicules sont créés indépendamment (ailleurs,
par exemple dans main.py) puis simplement rattachés à la flotte. La flotte
ne les possède pas au sens strict : leur cycle de vie ne dépend pas d'elle.
"""
from datetime import date

from models.enums import StatutVehicule, CategorieClient, StatutLocation
from models.location import Location


class Flotte:
    def __init__(self, nom: str = "Flotte principale"):
        self.nom = nom
        self.vehicules: list = []      # agrégation
        self.locations: list[Location] = []
        self._prochain_id_location = 1

    # ------------------------------------------------------------------ #
    # Gestion des véhicules (agrégation)
    # ------------------------------------------------------------------ #
    def ajouter_vehicule(self, vehicule) -> None:
        if self.trouver_vehicule(vehicule.immatriculation):
            raise ValueError(f"Un véhicule {vehicule.immatriculation} existe déjà dans la flotte")
        self.vehicules.append(vehicule)

    def retirer_vehicule(self, immatriculation: str) -> None:
        self.vehicules = [v for v in self.vehicules if v.immatriculation != immatriculation]

    def trouver_vehicule(self, immatriculation: str):
        return next((v for v in self.vehicules if v.immatriculation == immatriculation), None)

    def vehicules_par_type(self, type_classe) -> list:
        return [v for v in self.vehicules if isinstance(v, type_classe)]

    # ------------------------------------------------------------------ #
    # Fonctionnalité 17 : cycle complet d'une location
    # ------------------------------------------------------------------ #
    def creer_location(self, immatriculation: str, client_nom: str,
                        categorie_client: CategorieClient,
                        date_debut: date, date_fin_prevue: date) -> Location:
        vehicule = self.trouver_vehicule(immatriculation)
        if vehicule is None:
            raise ValueError(f"Véhicule {immatriculation} introuvable dans la flotte")

        location = Location(
            id_location=self._prochain_id_location,
            vehicule=vehicule,
            client_nom=client_nom,
            categorie_client=categorie_client,
            date_debut=date_debut,
            date_fin_prevue=date_fin_prevue,
        )
        self._prochain_id_location += 1
        self.locations.append(location)
        return location

    def demarrer_location(self, id_location: int, km_depart: int) -> Location:
        location = self._trouver_location(id_location)
        location.demarrer(km_depart)
        return location

    def cloturer_location(self, id_location: int, date_retour: date, km_retour: int) -> Location:
        location = self._trouver_location(id_location)
        location.cloturer(date_retour, km_retour)
        return location

    def _trouver_location(self, id_location: int) -> Location:
        location = next((l for l in self.locations if l.id_location == id_location), None)
        if location is None:
            raise ValueError(f"Location #{id_location} introuvable")
        return location

    # ------------------------------------------------------------------ #
    # Fonctionnalité 18 : détection des véhicules à entretenir
    # ------------------------------------------------------------------ #
    def vehicules_a_entretenir(self) -> list:
        return [v for v in self.vehicules if v.necessite_entretien()]

    # ------------------------------------------------------------------ #
    # Fonctionnalité 19 : rapport de disponibilité à une date donnée
    # ------------------------------------------------------------------ #
    def vehicules_disponibles(self, a_date: date = None) -> list:
        """Un véhicule est disponible à une date donnée s'il n'est pas
        HORS_SERVICE/EN_MAINTENANCE et n'est engagé dans aucune location
        (réservée ou en cours) qui chevauche cette date."""
        a_date = a_date or date.today()

        immats_occupees = set()
        for loc in self.locations:
            if loc.statut in (StatutLocation.RESERVEE, StatutLocation.EN_COURS):
                if loc.date_debut <= a_date <= loc.date_fin_prevue:
                    immats_occupees.add(loc.vehicule.immatriculation)

        return [
            v for v in self.vehicules
            if v.statut not in (StatutVehicule.EN_MAINTENANCE, StatutVehicule.HORS_SERVICE)
            and v.immatriculation not in immats_occupees
        ]

    def rapport_disponibilite(self, a_date: date = None) -> dict:
        a_date = a_date or date.today()
        disponibles = self.vehicules_disponibles(a_date)

        par_statut = {s: 0 for s in StatutVehicule}
        for v in self.vehicules:
            par_statut[v.statut] += 1

        return {
            "date": a_date.isoformat(),
            "total_vehicules": len(self.vehicules),
            "nb_disponibles": len(disponibles),
            "immatriculations_disponibles": [v.immatriculation for v in disponibles],
            "repartition_par_statut": {s.value: n for s, n in par_statut.items()},
            "vehicules_a_entretenir": [v.immatriculation for v in self.vehicules_a_entretenir()],
        }

    def afficher_rapport_disponibilite(self, a_date: date = None) -> None:
        rapport = self.rapport_disponibilite(a_date)
        print(f"\n=== Rapport de disponibilité — {rapport['date']} ===")
        print(f"Flotte totale       : {rapport['total_vehicules']} véhicule(s)")
        print(f"Disponibles         : {rapport['nb_disponibles']} véhicule(s)")
        for immat in rapport["immatriculations_disponibles"]:
            print(f"   - {immat}")
        print("Répartition par statut :")
        for statut, n in rapport["repartition_par_statut"].items():
            print(f"   {statut:<15}: {n}")
        if rapport["vehicules_a_entretenir"]:
            print(f"⚠ Véhicules nécessitant un entretien : {', '.join(rapport['vehicules_a_entretenir'])}")
        else:
            print("Aucun véhicule ne nécessite d'entretien immédiat.")

    def __repr__(self) -> str:
        return f"<Flotte '{self.nom}' - {len(self.vehicules)} véhicule(s), {len(self.locations)} location(s)>"
