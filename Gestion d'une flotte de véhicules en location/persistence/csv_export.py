"""
Export CSV des contrats de location (actifs ou clôturés) sur une période donnée.
"""
import csv
from datetime import date

from config.config import CSV_LOCATIONS_PATH
from models import Flotte
from models.enums import StatutLocation

CHAMPS_CSV = [
    "id_location", "immatriculation", "marque", "modele", "client_nom",
    "categorie_client", "date_debut", "date_fin_prevue", "date_retour_reelle",
    "km_depart", "km_retour", "statut", "tarif_jour_applique",
    "montant_total", "penalite_retard",
]


def exporter_locations_csv(flotte: Flotte, date_debut_periode: date, date_fin_periode: date,
                            statuts: list[StatutLocation] = None, chemin: str = None) -> str:
    """
    Exporte les locations dont la date de début tombe dans [date_debut_periode, date_fin_periode].
    `statuts` permet de filtrer (ex: [StatutLocation.EN_COURS] pour les actives,
    ou [StatutLocation.CLOTUREE] pour les clôturées). None = tous statuts.
    """
    chemin = chemin or CSV_LOCATIONS_PATH
    statuts = statuts or list(StatutLocation)

    lignes = [
        loc for loc in flotte.locations
        if date_debut_periode <= loc.date_debut <= date_fin_periode and loc.statut in statuts
    ]

    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CHAMPS_CSV, delimiter=";")
        writer.writeheader()
        for loc in lignes:
            writer.writerow({
                "id_location": loc.id_location,
                "immatriculation": loc.vehicule.immatriculation,
                "marque": loc.vehicule.marque,
                "modele": loc.vehicule.modele,
                "client_nom": loc.client_nom,
                "categorie_client": loc.categorie_client.value,
                "date_debut": loc.date_debut.isoformat(),
                "date_fin_prevue": loc.date_fin_prevue.isoformat(),
                "date_retour_reelle": loc.date_retour_reelle.isoformat() if loc.date_retour_reelle else "",
                "km_depart": loc.km_depart if loc.km_depart is not None else "",
                "km_retour": loc.km_retour if loc.km_retour is not None else "",
                "statut": loc.statut.value,
                "tarif_jour_applique": loc.tarif_jour_applique,
                "montant_total": loc.montant_total,
                "penalite_retard": loc.penalite_retard,
            })

    return chemin
