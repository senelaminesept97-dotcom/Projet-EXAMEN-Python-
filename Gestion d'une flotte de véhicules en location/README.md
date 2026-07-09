# Gestion d'une flotte de véhicules en location

Application Python (POO) de gestion d'une flotte hétérogène de véhicules
(voitures, utilitaires, motos) en location : contrats, disponibilité,
maintenance, et persistance (JSON, CSV, SQLite/MySQL).

## Arborescence

```
GFVL/
│
├── main.py                    # Script de démonstration (point d'entrée)
│
├── models/                    # Domaine métier (POO)
│   ├── enums.py                #  StatutVehicule, CategorieClient, StatutLocation
│   ├── entretien.py            #  Entretien (composition)
│   ├── vehicule.py             #  VehiculeBase (ABC), Voiture, Utilitaire, Moto
│   ├── location.py             #  Location (contrat de location)
│   └── flotte.py               #  Flotte (agrégation de véhicules)
│
├── persistence/                # Export / import fichiers
│   ├── json_export.py          #  export/import JSON de l'état complet
│   └── csv_export.py           #  export CSV des contrats de location
│
├── db/
│   ├── connection.py           # Connexion SQLite (par défaut) ou MySQL
│   └── operations.py           # Création des tables + requêtes métier
│
├── config/
│   └── config.py               # Chemins, moteur de BDD, constantes métier
│
├── utils/
│   └── helpers.py               # Fonctions d'affichage / formatage
│
├── data/                        # Fichiers générés (JSON, CSV, flotte.db)
└── README.md
```

> Remarque : l'énoncé imposait `main.py`, `db/`, `config/`, `utils/` et le
> README. Deux dossiers ont été ajoutés pour respecter proprement la
> hiérarchie de classes et les règles de persistance demandées :
> `models/` (classes métier) et `persistence/` (export JSON/CSV). Les mettre
> directement dans `utils/` ou `main.py` aurait mélangé les responsabilités.

## Hiérarchie de classes

```
VehiculeBase (ABC)
 ├── calculer_tarif_jour(categorie_client)   [abstrait]
 ├── necessite_entretien()                   [abstrait]
 │
 ├── Voiture      (nb_places, categorie: CITADINE/BERLINE/SUV)
 ├── Utilitaire   (charge_utile_kg, volume_m3)
 └── Moto         (cylindree_cm3)
```

- **Enum `StatutVehicule`** : `DISPONIBLE`, `LOUE`, `EN_MAINTENANCE`, `HORS_SERVICE`
- **Enum `CategorieClient`** : `PARTICULIER`, `ENTREPRISE`, `EVENEMENTIEL`
  (utilisée comme coefficient multiplicateur du tarif journalier)

### Devise

Tous les montants (tarifs journaliers, chiffre d'affaires, pénalités,
coûts d'entretien) sont exprimés en **Francs CFA (FCFA / XOF)**, sans
sous-unité décimale (conformément à l'usage courant de cette devise).
Voir `config/config.py` (`DEVISE`, `PENALITE_PAR_JOUR_RETARD`) et
`utils/helpers.py` (`formater_montant`).

### Relations

- **Agrégation** — `Flotte.vehicules` : les véhicules sont créés indépendamment
  (dans `main.py`) puis simplement rattachés à la flotte via
  `flotte.ajouter_vehicule(...)`. Leur cycle de vie ne dépend pas de la flotte.
- **Composition** — `VehiculeBase._historique_entretien` : chaque véhicule crée
  lui-même ses objets `Entretien` via `vehicule.ajouter_entretien(...)`. Un
  `Entretien` n'existe jamais indépendamment de son véhicule.

## Fonctionnalités

| # | Fonctionnalité | Où |
|---|---|---|
| 16 | Flotte mixte (8 véhicules, 3 types) | `main.creer_flotte_demo()` |
| 17 | Cycle complet de location (réservation → départ → retour, tarif selon durée/catégorie) | `models.Location`, `models.Flotte.creer_location/demarrer_location/cloturer_location` |
| 18 | Détection automatique des véhicules à entretenir (seuil km ou date) | `VehiculeBase.necessite_entretien()`, `Flotte.vehicules_a_entretenir()` |
| 19 | Rapport de disponibilité à une date donnée | `Flotte.rapport_disponibilite()` / `afficher_rapport_disponibilite()` |
| 20 | Bonus : pénalité de retour tardif | `Location.cloturer()` (25 €/jour de retard, configurable dans `config.py`) |

## Persistance

- **JSON** : `persistence/json_export.py`
  `exporter_flotte_json(flotte)` / `importer_flotte_json(chemin)`
  exporte/reconstruit l'état complet (véhicules + historiques d'entretien + locations).

- **CSV** : `persistence/csv_export.py`
  `exporter_locations_csv(flotte, date_debut, date_fin, statuts=None)`
  exporte les contrats de location (actifs et/ou clôturés) sur une période.

- **SQLite / MySQL** : `db/connection.py` + `db/operations.py`
  - Tables : `vehicules`, `locations` (FK vers `vehicules`), `entretiens`.
  - `creer_tables(conn)`, `synchroniser_flotte(conn, flotte)`
  - Requêtes métier :
    - `vehicules_disponibles_a_date(conn, a_date)`
    - `chiffre_affaires_par_categorie(conn)` (regroupé par type de véhicule)
    - `historique_entretien_vehicule(conn, immatriculation)`

  Par défaut le projet utilise **SQLite** (fichier `data/flotte.db`, aucune
  dépendance externe). Pour basculer vers **MySQL** :
  1. `pip install mysql-connector-python`
  2. dans `config/config.py`, mettre `DB_ENGINE = "mysql"` (ou variable
     d'environnement `DB_ENGINE=mysql`) et renseigner `MYSQL_CONFIG`.

## Lancer le projet

```bash
cd mon_projet
python3 main.py
```

Le script exécute une démonstration complète : création de la flotte,
locations (dont une avec pénalité de retard), détection des entretiens,
rapport de disponibilité, puis export JSON/CSV et synchronisation +
requêtes SQLite. Les fichiers générés se trouvent dans `data/`.

## Prérequis

- Python ≥ 3.10 (utilisation de `list[Entretien]`, `date | None`)
- Aucune dépendance externe requise pour SQLite (module standard `sqlite3`)
