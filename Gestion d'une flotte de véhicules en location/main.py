"""
Script principal de démonstration.

Illustre les 5 fonctionnalités demandées :
 16. Création d'une flotte mixte (>= 8 véhicules, 3 types).
 17. Cycle complet d'une location (réservation, départ, retour, tarif).
 18. Détection automatique des véhicules à entretenir.
 19. Rapport de disponibilité de la flotte à une date donnée.
 20. Bonus : pénalité de retour tardif.

Persistance illustrée : export/import JSON, export CSV, synchronisation
et requêtes SQLite.
"""
from datetime import date, timedelta

from models import Flotte, Voiture, Utilitaire, Moto, CategorieClient, StatutVehicule
from models.enums import StatutLocation
from persistence.json_export import exporter_flotte_json, importer_flotte_json
from persistence.csv_export import exporter_locations_csv
from db.connection import ConnexionDB
from db import operations as db_ops
from utils.helpers import afficher_titre, afficher_tableau, formater_montant, formater_date


# ============================================================================
# 16. Création d'une flotte mixte (8+ véhicules, 3 types)
# ============================================================================
def creer_flotte_demo() -> Flotte:
    flotte = Flotte("Flotte Dakar Location")

    vehicules = [
        Voiture("AA-123-BB", "Renault", "Clio", nb_places=5, categorie="CITADINE", kilometrage=8_500),
        Voiture("AB-456-CC", "Peugeot", "308", nb_places=5, categorie="BERLINE", kilometrage=22_000),
        Voiture("AC-789-DD", "Toyota", "RAV4", nb_places=5, categorie="SUV", kilometrage=15_200),
        Voiture("AD-321-EE", "Dacia", "Sandero", nb_places=5, categorie="CITADINE", kilometrage=41_000),
        Utilitaire("BA-111-FF", "Renault", "Master", charge_utile_kg=1200, volume_m3=12, kilometrage=33_500),
        Utilitaire("BB-222-GG", "Ford", "Transit", charge_utile_kg=1500, volume_m3=15, kilometrage=9_800),
        Moto("CA-333-HH", "Yamaha", "MT-07", cylindree_cm3=689, kilometrage=6_200),
        Moto("CB-444-II", "Honda", "PCX 125", cylindree_cm3=125, kilometrage=12_500),
    ]

    for v in vehicules:
        flotte.ajouter_vehicule(v)

    # On force volontairement deux véhicules en seuil d'entretien pour la démo
    flotte.trouver_vehicule("AD-321-EE").kilometrage = 41_000  # > seuil 10 000 km depuis 0
    flotte.trouver_vehicule("BA-111-FF").date_dernier_entretien = date.today() - timedelta(days=200)

    return flotte


# ============================================================================
# 17. Cycle complet d'une location + 20. Pénalité de retard (bonus)
# ============================================================================
def demo_cycle_location(flotte: Flotte) -> None:
    afficher_titre("17. Cycle complet d'une location")

    # --- Location A : particulier, dans les temps ---
    loc_a = flotte.creer_location(
        immatriculation="AA-123-BB",
        client_nom="Fatou Ndiaye",
        categorie_client=CategorieClient.PARTICULIER,
        date_debut=date.today() - timedelta(days=5),
        date_fin_prevue=date.today() - timedelta(days=1),
    )
    loc_a.demarrer(km_depart=8_500)
    montant_a = loc_a.cloturer(date_retour=date.today() - timedelta(days=1), km_retour=8_720)
    print(f"Location #{loc_a.id_location} ({loc_a.client_nom}) : "
          f"{formater_montant(montant_a)} — retour à l'heure, pénalité = {formater_montant(loc_a.penalite_retard)}")

    # --- Location B : entreprise, retour tardif -> pénalité (bonus) ---
    loc_b = flotte.creer_location(
        immatriculation="BB-222-GG",
        client_nom="SenLogistics SARL",
        categorie_client=CategorieClient.ENTREPRISE,
        date_debut=date.today() - timedelta(days=10),
        date_fin_prevue=date.today() - timedelta(days=4),
    )
    loc_b.demarrer(km_depart=9_800)
    montant_b = loc_b.cloturer(date_retour=date.today() - timedelta(days=1), km_retour=10_400)
    print(f"Location #{loc_b.id_location} ({loc_b.client_nom}) : "
          f"{formater_montant(montant_b)} — retour avec 3 jour(s) de retard, "
          f"pénalité = {formater_montant(loc_b.penalite_retard)}")

    # --- Location C : événementiel, en cours (non clôturée) ---
    loc_c = flotte.creer_location(
        immatriculation="CA-333-HH",
        client_nom="Agence Teranga Events",
        categorie_client=CategorieClient.EVENEMENTIEL,
        date_debut=date.today(),
        date_fin_prevue=date.today() + timedelta(days=2),
    )
    loc_c.demarrer(km_depart=6_200)
    print(f"Location #{loc_c.id_location} ({loc_c.client_nom}) : en cours, "
          f"tarif/jour = {formater_montant(loc_c.vehicule.calculer_tarif_jour(loc_c.categorie_client))}")


# ============================================================================
# 18. Détection automatique des véhicules à entretenir
# ============================================================================
def demo_detection_entretien(flotte: Flotte) -> None:
    afficher_titre("18. Véhicules nécessitant un entretien")
    a_entretenir = flotte.vehicules_a_entretenir()
    if not a_entretenir:
        print("Aucun véhicule ne nécessite d'entretien.")
        return

    lignes = [[v.immatriculation, v.__class__.__name__, v.marque, v.modele, v.kilometrage]
              for v in a_entretenir]
    afficher_tableau(lignes, entetes=["Immatriculation", "Type", "Marque", "Modèle", "Kilométrage"])

    # On effectue l'entretien du premier véhicule détecté, pour illustrer ajouter_entretien()
    vehicule = a_entretenir[0]
    vehicule.statut = StatutVehicule.EN_MAINTENANCE
    entretien = vehicule.ajouter_entretien("Révision complète", cout=75_000.0,
                                            description="Vidange + contrôle freins/pneus")
    print(f"\n-> Entretien réalisé sur {vehicule.immatriculation} : {entretien}")
    print(f"   Nouveau statut : {vehicule.statut.value}")


# ============================================================================
# 19. Rapport de disponibilité à une date donnée
# ============================================================================
def demo_rapport_disponibilite(flotte: Flotte) -> None:
    afficher_titre("19. Rapport de disponibilité de la flotte")
    flotte.afficher_rapport_disponibilite(date.today())


# ============================================================================
# Persistance : JSON, CSV, SQLite
# ============================================================================
def demo_persistance(flotte: Flotte) -> None:
    afficher_titre("Persistance : JSON / CSV / SQLite")

    # --- JSON : export puis ré-import complet ---
    chemin_json = exporter_flotte_json(flotte)
    print(f"[JSON] Export de la flotte -> {chemin_json}")
    flotte_reimportee = importer_flotte_json(chemin_json)
    print(f"[JSON] Ré-import OK -> {flotte_reimportee}")

    # --- CSV : export des locations sur les 30 derniers jours ---
    chemin_csv = exporter_locations_csv(
        flotte,
        date_debut_periode=date.today() - timedelta(days=30),
        date_fin_periode=date.today() + timedelta(days=30),
    )
    print(f"[CSV]  Export des locations -> {chemin_csv}")

    # --- SQLite : création des tables + synchronisation + requêtes métier ---
    with ConnexionDB() as conn:
        db_ops.creer_tables(conn)
        db_ops.synchroniser_flotte(conn, flotte)
    print(f"[SQL]  Tables créées et synchronisées ({db_ops.__name__})")

    with ConnexionDB() as conn:
        afficher_titre("SQL — Véhicules disponibles aujourd'hui")
        rows = db_ops.vehicules_disponibles_a_date(conn, date.today())
        lignes = [[r["immatriculation"], r["type_vehicule"], r["marque"], r["modele"], r["statut"]]
                  for r in rows]
        afficher_tableau(lignes, entetes=["Immatriculation", "Type", "Marque", "Modèle", "Statut"])

        afficher_titre("SQL — Chiffre d'affaires par catégorie de véhicule")
        rows = db_ops.chiffre_affaires_par_categorie(conn)
        lignes = [[r["categorie_vehicule"], r["nb_locations"],
                   formater_montant(r["chiffre_affaires"]), formater_montant(r["total_penalites"])]
                  for r in rows]
        afficher_tableau(lignes, entetes=["Type", "Nb locations", "CA total", "Dont pénalités"])

        afficher_titre("SQL — Historique d'entretien (BA-111-FF)")
        rows = db_ops.historique_entretien_vehicule(conn, "BA-111-FF")
        if rows:
            lignes = [[r["date_entretien"], r["type_entretien"], r["kilometrage"], formater_montant(r["cout"])]
                      for r in rows]
            afficher_tableau(lignes, entetes=["Date", "Type", "Kilométrage", "Coût"])
        else:
            print("Aucun entretien enregistré pour ce véhicule.")


def main() -> None:
    afficher_titre("16. Création de la flotte mixte")
    flotte = creer_flotte_demo()
    print(f"{flotte} — {len(flotte.vehicules_par_type(Voiture))} voiture(s), "
          f"{len(flotte.vehicules_par_type(Utilitaire))} utilitaire(s), "
          f"{len(flotte.vehicules_par_type(Moto))} moto(s)")

    demo_cycle_location(flotte)
    demo_detection_entretien(flotte)
    demo_rapport_disponibilite(flotte)
    demo_persistance(flotte)

    afficher_titre("Démonstration terminée")


if __name__ == "__main__":
    main()
