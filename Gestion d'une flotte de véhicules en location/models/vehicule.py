"""
Hiérarchie des véhicules de la flotte.

VehiculeBase (ABC)
 ├── Voiture
 ├── Utilitaire
 └── Moto

Relation de COMPOSITION : chaque véhicule crée et possède son propre
historique d'Entretien (_historique_entretien). Les objets Entretien
n'existent jamais indépendamment d'un véhicule.
"""
from abc import ABC, abstractmethod
from datetime import date

from models.enums import StatutVehicule, CategorieClient
from models.entretien import Entretien


# Coefficients tarifaires communs, appliqués selon la catégorie du client
COEFFICIENTS_CLIENT = {
    CategorieClient.PARTICULIER: 1.00,
    CategorieClient.ENTREPRISE: 0.85,   # tarif négocié, volume
    CategorieClient.EVENEMENTIEL: 1.30,  # location courte, forte demande
}


class VehiculeBase(ABC):
    """Classe abstraite commune à tous les véhicules de la flotte."""

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 kilometrage: int = 0, statut: StatutVehicule = StatutVehicule.DISPONIBLE,
                 date_dernier_entretien: date = None):
        self.immatriculation = immatriculation
        self.marque = marque
        self.modele = modele
        self.kilometrage = kilometrage
        self.statut = statut
        self.date_dernier_entretien = date_dernier_entretien or date.today()
        self._historique_entretien: list[Entretien] = []  # composition

    # ------------------------------------------------------------------ #
    # Méthodes abstraites imposées par l'énoncé
    # ------------------------------------------------------------------ #
    @abstractmethod
    def calculer_tarif_jour(self, categorie_client: CategorieClient) -> float:
        """Retourne le tarif journalier (en Francs CFA / XOF) selon la catégorie du client."""
        raise NotImplementedError

    @abstractmethod
    def necessite_entretien(self) -> bool:
        """Retourne True si un entretien est requis (seuil km ou date dépassé)."""
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Gestion de l'historique d'entretien (composition)
    # ------------------------------------------------------------------ #
    def ajouter_entretien(self, type_entretien: str, cout: float, description: str = "") -> Entretien:
        """Crée un nouvel Entretien pour CE véhicule et l'ajoute à son historique."""
        entretien = Entretien(
            date_entretien=date.today(),
            type_entretien=type_entretien,
            kilometrage=self.kilometrage,
            cout=cout,
            description=description,
        )
        self._historique_entretien.append(entretien)
        self.date_dernier_entretien = entretien.date_entretien
        if self.statut == StatutVehicule.EN_MAINTENANCE:
            self.statut = StatutVehicule.DISPONIBLE
        return entretien

    @property
    def historique_entretien(self) -> list:
        """Copie en lecture seule de l'historique d'entretien du véhicule."""
        return list(self._historique_entretien)

    def _km_depuis_dernier_entretien(self) -> int:
        if self._historique_entretien:
            return self.kilometrage - self._historique_entretien[-1].kilometrage
        return self.kilometrage

    def _jours_depuis_dernier_entretien(self) -> int:
        return (date.today() - self.date_dernier_entretien).days

    # ------------------------------------------------------------------ #
    # Sérialisation
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "immatriculation": self.immatriculation,
            "marque": self.marque,
            "modele": self.modele,
            "kilometrage": self.kilometrage,
            "statut": self.statut.value,
            "date_dernier_entretien": self.date_dernier_entretien.isoformat(),
            "historique_entretien": [e.to_dict() for e in self._historique_entretien],
            **self._attrs_specifiques(),
        }

    def _attrs_specifiques(self) -> dict:
        """À redéfinir dans les sous-classes pour ajouter leurs attributs propres."""
        return {}

    def __repr__(self) -> str:
        return (f"<{self.__class__.__name__} {self.immatriculation} "
                f"{self.marque} {self.modele} - {self.statut.value}>")


class Voiture(VehiculeBase):
    """Voiture particulière : citadine, berline ou SUV."""

    SEUIL_KM_ENTRETIEN = 10_000
    SEUIL_JOURS_ENTRETIEN = 180

    # Tarifs journaliers en Francs CFA (XOF)
    TARIFS_BASE = {
        "CITADINE": 20_000.0,
        "BERLINE": 35_000.0,
        "SUV": 50_000.0,
    }

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 nb_places: int, categorie: str = "CITADINE", **kwargs):
        super().__init__(immatriculation, marque, modele, **kwargs)
        self.nb_places = nb_places
        self.categorie = categorie.upper()

    def calculer_tarif_jour(self, categorie_client: CategorieClient) -> float:
        base = self.TARIFS_BASE.get(self.categorie, 27_000.0)
        coef = COEFFICIENTS_CLIENT[categorie_client]
        return round(base * coef, 2)

    def necessite_entretien(self) -> bool:
        return (self._km_depuis_dernier_entretien() >= self.SEUIL_KM_ENTRETIEN
                or self._jours_depuis_dernier_entretien() >= self.SEUIL_JOURS_ENTRETIEN)

    def _attrs_specifiques(self) -> dict:
        return {"nb_places": self.nb_places, "categorie": self.categorie}


class Utilitaire(VehiculeBase):
    """Véhicule utilitaire léger (fourgon, camionnette)."""

    SEUIL_KM_ENTRETIEN = 15_000   # usage plus intensif -> seuil plus élevé
    SEUIL_JOURS_ENTRETIEN = 120   # mais contrôle plus fréquent (charge lourde)

    # Tarifs journaliers en Francs CFA (XOF)
    TARIF_BASE = 40_000.0
    TARIF_PAR_TONNE = 5_000.0

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 charge_utile_kg: float, volume_m3: float, **kwargs):
        super().__init__(immatriculation, marque, modele, **kwargs)
        self.charge_utile_kg = charge_utile_kg
        self.volume_m3 = volume_m3

    def calculer_tarif_jour(self, categorie_client: CategorieClient) -> float:
        base = self.TARIF_BASE + (self.charge_utile_kg / 1000) * self.TARIF_PAR_TONNE
        coef = COEFFICIENTS_CLIENT[categorie_client]
        return round(base * coef, 2)

    def necessite_entretien(self) -> bool:
        return (self._km_depuis_dernier_entretien() >= self.SEUIL_KM_ENTRETIEN
                or self._jours_depuis_dernier_entretien() >= self.SEUIL_JOURS_ENTRETIEN)

    def _attrs_specifiques(self) -> dict:
        return {"charge_utile_kg": self.charge_utile_kg, "volume_m3": self.volume_m3}


class Moto(VehiculeBase):
    """Moto ou scooter."""

    SEUIL_KM_ENTRETIEN = 8_000
    SEUIL_JOURS_ENTRETIEN = 150

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 cylindree_cm3: int, **kwargs):
        super().__init__(immatriculation, marque, modele, **kwargs)
        self.cylindree_cm3 = cylindree_cm3

    def calculer_tarif_jour(self, categorie_client: CategorieClient) -> float:
        # Tarifs journaliers en Francs CFA (XOF)
        if self.cylindree_cm3 <= 125:
            base = 10_000.0
        elif self.cylindree_cm3 <= 500:
            base = 18_000.0
        else:
            base = 28_000.0
        coef = COEFFICIENTS_CLIENT[categorie_client]
        return round(base * coef, 2)

    def necessite_entretien(self) -> bool:
        return (self._km_depuis_dernier_entretien() >= self.SEUIL_KM_ENTRETIEN
                or self._jours_depuis_dernier_entretien() >= self.SEUIL_JOURS_ENTRETIEN)

    def _attrs_specifiques(self) -> dict:
        return {"cylindree_cm3": self.cylindree_cm3}


# ---------------------------------------------------------------------- #
# Fabrique utilitaire pour reconstruire un véhicule depuis un dict (JSON)
# ---------------------------------------------------------------------- #
def vehicule_from_dict(d: dict) -> VehiculeBase:
    type_ = d["type"]
    commun = dict(
        immatriculation=d["immatriculation"],
        marque=d["marque"],
        modele=d["modele"],
        kilometrage=d["kilometrage"],
        statut=StatutVehicule(d["statut"]),
        date_dernier_entretien=date.fromisoformat(d["date_dernier_entretien"]),
    )
    if type_ == "Voiture":
        vehicule = Voiture(nb_places=d["nb_places"], categorie=d["categorie"], **commun)
    elif type_ == "Utilitaire":
        vehicule = Utilitaire(charge_utile_kg=d["charge_utile_kg"], volume_m3=d["volume_m3"], **commun)
    elif type_ == "Moto":
        vehicule = Moto(cylindree_cm3=d["cylindree_cm3"], **commun)
    else:
        raise ValueError(f"Type de véhicule inconnu: {type_}")

    vehicule._historique_entretien = [Entretien.from_dict(e) for e in d.get("historique_entretien", [])]
    return vehicule
