"""
Classe Location : représente un contrat de location d'un véhicule.

Cycle complet : réservation -> départ (démarrer) -> retour (cloturer),
avec calcul du tarif selon la durée et la catégorie client, et calcul
d'une pénalité en cas de retour tardif (bonus fonctionnalité 20).
"""
from datetime import date

from models.enums import StatutVehicule, CategorieClient, StatutLocation


class Location:
    PENALITE_PAR_JOUR_RETARD = 15_000.0  # FCFA par jour de retard

    def __init__(self, id_location: int, vehicule, client_nom: str,
                 categorie_client: CategorieClient, date_debut: date, date_fin_prevue: date):
        if date_fin_prevue < date_debut:
            raise ValueError("La date de fin prévue ne peut pas précéder la date de début")

        self.id_location = id_location
        self.vehicule = vehicule
        self.client_nom = client_nom
        self.categorie_client = categorie_client
        self.date_debut = date_debut
        self.date_fin_prevue = date_fin_prevue

        self.date_retour_reelle: date | None = None
        self.km_depart: int | None = None
        self.km_retour: int | None = None

        self.statut = StatutLocation.RESERVEE
        self.tarif_jour_applique: float = 0.0
        self.montant_total: float = 0.0
        self.penalite_retard: float = 0.0

    # ------------------------------------------------------------------ #
    # Cycle de vie
    # ------------------------------------------------------------------ #
    def demarrer(self, km_depart: int, date_depart_reelle: date = None) -> None:
        """Marque le départ effectif du véhicule (remise des clés au client)."""
        if self.statut != StatutLocation.RESERVEE:
            raise ValueError(f"Impossible de démarrer une location au statut {self.statut.value}")
        if self.vehicule.statut != StatutVehicule.DISPONIBLE:
            raise ValueError(f"Véhicule {self.vehicule.immatriculation} non disponible "
                              f"(statut actuel: {self.vehicule.statut.value})")

        self.km_depart = km_depart
        self.date_debut = date_depart_reelle or self.date_debut
        self.vehicule.statut = StatutVehicule.LOUE
        self.statut = StatutLocation.EN_COURS

    def cloturer(self, date_retour: date, km_retour: int) -> float:
        """Marque le retour du véhicule, calcule le tarif final + pénalité éventuelle."""
        if self.statut != StatutLocation.EN_COURS:
            raise ValueError(f"Impossible de clôturer une location au statut {self.statut.value}")
        if km_retour < self.km_depart:
            raise ValueError("Le kilométrage de retour ne peut pas être inférieur au kilométrage de départ")

        self.date_retour_reelle = date_retour
        self.km_retour = km_retour
        self.vehicule.kilometrage = km_retour

        duree_jours = max((self.date_fin_prevue - self.date_debut).days, 1)
        self.tarif_jour_applique = self.vehicule.calculer_tarif_jour(self.categorie_client)
        self.montant_total = round(self.tarif_jour_applique * duree_jours, 2)

        # --- Bonus : pénalité de retard ---
        if date_retour > self.date_fin_prevue:
            jours_retard = (date_retour - self.date_fin_prevue).days
            self.penalite_retard = round(jours_retard * self.PENALITE_PAR_JOUR_RETARD, 2)
            self.montant_total = round(self.montant_total + self.penalite_retard, 2)

        self.statut = StatutLocation.CLOTUREE

        # Le véhicule repasse disponible, sauf s'il a besoin d'un entretien
        if self.vehicule.necessite_entretien():
            self.vehicule.statut = StatutVehicule.EN_MAINTENANCE
        else:
            self.vehicule.statut = StatutVehicule.DISPONIBLE

        return self.montant_total

    def annuler(self) -> None:
        if self.statut != StatutLocation.RESERVEE:
            raise ValueError("Seule une location réservée (non démarrée) peut être annulée")
        self.statut = StatutLocation.ANNULEE

    # ------------------------------------------------------------------ #
    # Sérialisation
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return {
            "id_location": self.id_location,
            "immatriculation_vehicule": self.vehicule.immatriculation,
            "client_nom": self.client_nom,
            "categorie_client": self.categorie_client.value,
            "date_debut": self.date_debut.isoformat(),
            "date_fin_prevue": self.date_fin_prevue.isoformat(),
            "date_retour_reelle": self.date_retour_reelle.isoformat() if self.date_retour_reelle else None,
            "km_depart": self.km_depart,
            "km_retour": self.km_retour,
            "statut": self.statut.value,
            "tarif_jour_applique": self.tarif_jour_applique,
            "montant_total": self.montant_total,
            "penalite_retard": self.penalite_retard,
        }

    def __repr__(self) -> str:
        return (f"<Location #{self.id_location} {self.vehicule.immatriculation} "
                f"client={self.client_nom} statut={self.statut.value}>")
