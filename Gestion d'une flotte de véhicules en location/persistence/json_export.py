"""
Export / import de l'état complet de la flotte au format JSON.
"""
import json

from config.config import JSON_EXPORT_PATH
from models import Flotte, CategorieClient, vehicule_from_dict
from models.location import Location


def exporter_flotte_json(flotte: Flotte, chemin: str = None) -> str:
    """Sérialise la flotte entière (véhicules + historiques + locations) en JSON."""
    chemin = chemin or JSON_EXPORT_PATH
    data = {
        "nom_flotte": flotte.nom,
        "vehicules": [v.to_dict() for v in flotte.vehicules],
        "locations": [l.to_dict() for l in flotte.locations],
    }
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return chemin


def importer_flotte_json(chemin: str = None) -> Flotte:
    """Reconstruit un objet Flotte complet à partir d'un export JSON."""
    chemin = chemin or JSON_EXPORT_PATH
    with open(chemin, "r", encoding="utf-8") as f:
        data = json.load(f)

    flotte = Flotte(nom=data.get("nom_flotte", "Flotte importée"))

    for v_dict in data.get("vehicules", []):
        flotte.ajouter_vehicule(vehicule_from_dict(v_dict))

    from datetime import date
    max_id = 0
    for l_dict in data.get("locations", []):
        vehicule = flotte.trouver_vehicule(l_dict["immatriculation_vehicule"])
        if vehicule is None:
            continue
        location = Location(
            id_location=l_dict["id_location"],
            vehicule=vehicule,
            client_nom=l_dict["client_nom"],
            categorie_client=CategorieClient(l_dict["categorie_client"]),
            date_debut=date.fromisoformat(l_dict["date_debut"]),
            date_fin_prevue=date.fromisoformat(l_dict["date_fin_prevue"]),
        )
        location.km_depart = l_dict["km_depart"]
        location.km_retour = l_dict["km_retour"]
        location.date_retour_reelle = (
            date.fromisoformat(l_dict["date_retour_reelle"]) if l_dict["date_retour_reelle"] else None
        )
        from models.enums import StatutLocation
        location.statut = StatutLocation(l_dict["statut"])
        location.tarif_jour_applique = l_dict["tarif_jour_applique"]
        location.montant_total = l_dict["montant_total"]
        location.penalite_retard = l_dict["penalite_retard"]

        flotte.locations.append(location)
        max_id = max(max_id, location.id_location)

    flotte._prochain_id_location = max_id + 1
    return flotte
