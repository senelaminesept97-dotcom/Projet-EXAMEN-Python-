"""
Configuration centralisée du projet.
"""
import os

# Racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- Base de données ---
# SQLite par défaut (aucune dépendance externe). Pour basculer sur MySQL,
# changer DB_ENGINE à "mysql" et renseigner les paramètres MYSQL_*.
DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite")

SQLITE_DB_PATH = os.path.join(DATA_DIR, "flotte.db")

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "flotte_location"),
}

# --- Fichiers d'export ---
JSON_EXPORT_PATH = os.path.join(DATA_DIR, "flotte_export.json")
CSV_LOCATIONS_PATH = os.path.join(DATA_DIR, "locations_export.csv")

# --- Règles métier ---
DEVISE = "FCFA"  # Franc CFA (XOF)
PENALITE_PAR_JOUR_RETARD = 15_000.0  # en FCFA
