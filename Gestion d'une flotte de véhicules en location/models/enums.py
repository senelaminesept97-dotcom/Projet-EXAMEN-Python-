"""
Énumérations utilisées dans tout le projet.
"""
from enum import Enum


class StatutVehicule(Enum):
    """État courant d'un véhicule dans la flotte."""
    DISPONIBLE = "DISPONIBLE"
    LOUE = "LOUE"
    EN_MAINTENANCE = "EN_MAINTENANCE"
    HORS_SERVICE = "HORS_SERVICE"


class CategorieClient(Enum):
    """Catégorie du client, utilisée pour moduler le tarif journalier."""
    PARTICULIER = "PARTICULIER"
    ENTREPRISE = "ENTREPRISE"
    EVENEMENTIEL = "EVENEMENTIEL"


class StatutLocation(Enum):
    """Cycle de vie d'un contrat de location."""
    RESERVEE = "RESERVEE"
    EN_COURS = "EN_COURS"
    CLOTUREE = "CLOTUREE"
    ANNULEE = "ANNULEE"
