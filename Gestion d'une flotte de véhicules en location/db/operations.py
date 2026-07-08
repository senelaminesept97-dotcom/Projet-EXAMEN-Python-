"""
Opérations SQL sur la base de données : création du schéma, synchronisation
depuis les objets métier (Flotte), et requêtes métier demandées :
  - véhicules disponibles à une date donnée
  - chiffre d'affaires par catégorie de véhicule
  - historique d'entretien par véhicule
"""
from datetime import date

from db.connection import ConnexionDB
from models import Flotte
from models.enums import StatutLocation


# ========================================================================
# Création du schéma
# ========================================================================
def creer_tables(conn) -> None:
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicules (
            immatriculation        TEXT PRIMARY KEY,
            type_vehicule           TEXT NOT NULL,
            marque                  TEXT NOT NULL,
            modele                  TEXT NOT NULL,
            kilometrage             INTEGER NOT NULL,
            statut                  TEXT NOT NULL,
            date_dernier_entretien  TEXT NOT NULL,
            attribut_1              TEXT,
            attribut_2              TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id_location             INTEGER PRIMARY KEY,
            immatriculation         TEXT NOT NULL,
            client_nom              TEXT NOT NULL,
            categorie_client        TEXT NOT NULL,
            date_debut              TEXT NOT NULL,
            date_fin_prevue         TEXT NOT NULL,
            date_retour_reelle      TEXT,
            km_depart               INTEGER,
            km_retour               INTEGER,
            statut                  TEXT NOT NULL,
            tarif_jour_applique     REAL,
            montant_total           REAL,
            penalite_retard         REAL,
            FOREIGN KEY (immatriculation) REFERENCES vehicules(immatriculation)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entretiens (
            id_entretien       INTEGER PRIMARY KEY AUTOINCREMENT,
            immatriculation    TEXT NOT NULL,
            date_entretien      TEXT NOT NULL,
            type_entretien      TEXT NOT NULL,
            kilometrage         INTEGER NOT NULL,
            cout                REAL NOT NULL,
            description         TEXT,
            FOREIGN KEY (immatriculation) REFERENCES vehicules(immatriculation)
        )
    """)
    conn.commit()


# ========================================================================
# Synchronisation objets métier -> base de données
# ========================================================================
def synchroniser_flotte(conn, flotte: Flotte) -> None:
    """Vide puis réinsère l'intégralité des données de la flotte (simple et sûr
    pour un projet pédagogique ; une vraie appli ferait un upsert incrémental)."""
    cur = conn.cursor()
    cur.execute("DELETE FROM entretiens")
    cur.execute("DELETE FROM locations")
    cur.execute("DELETE FROM vehicules")

    for v in flotte.vehicules:
        attrs = v._attrs_specifiques()
        valeurs_attrs = list(attrs.values())
        attribut_1 = str(valeurs_attrs[0]) if len(valeurs_attrs) > 0 else None
        attribut_2 = str(valeurs_attrs[1]) if len(valeurs_attrs) > 1 else None

        cur.execute("""
            INSERT INTO vehicules (immatriculation, type_vehicule, marque, modele,
                                    kilometrage, statut, date_dernier_entretien,
                                    attribut_1, attribut_2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (v.immatriculation, v.__class__.__name__, v.marque, v.modele,
              v.kilometrage, v.statut.value, v.date_dernier_entretien.isoformat(),
              attribut_1, attribut_2))

        for e in v.historique_entretien:
            cur.execute("""
                INSERT INTO entretiens (immatriculation, date_entretien, type_entretien,
                                         kilometrage, cout, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (v.immatriculation, e.date_entretien.isoformat(), e.type_entretien,
                  e.kilometrage, e.cout, e.description))

    for loc in flotte.locations:
        cur.execute("""
            INSERT INTO locations (id_location, immatriculation, client_nom, categorie_client,
                                    date_debut, date_fin_prevue, date_retour_reelle,
                                    km_depart, km_retour, statut, tarif_jour_applique,
                                    montant_total, penalite_retard)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (loc.id_location, loc.vehicule.immatriculation, loc.client_nom,
              loc.categorie_client.value, loc.date_debut.isoformat(), loc.date_fin_prevue.isoformat(),
              loc.date_retour_reelle.isoformat() if loc.date_retour_reelle else None,
              loc.km_depart, loc.km_retour, loc.statut.value,
              loc.tarif_jour_applique, loc.montant_total, loc.penalite_retard))

    conn.commit()


# ========================================================================
# Requêtes métier
# ========================================================================
def vehicules_disponibles_a_date(conn, a_date: date) -> list:
    """Véhicules DISPONIBLES à une date donnée (statut ok + pas de location
    réservée/en cours qui chevauche la date)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT v.*
        FROM vehicules v
        WHERE v.statut NOT IN ('EN_MAINTENANCE', 'HORS_SERVICE')
          AND v.immatriculation NOT IN (
              SELECT l.immatriculation
              FROM locations l
              WHERE l.statut IN ('RESERVEE', 'EN_COURS')
                AND date(?) BETWEEN date(l.date_debut) AND date(l.date_fin_prevue)
          )
        ORDER BY v.immatriculation
    """, (a_date.isoformat(),))
    return cur.fetchall()


def chiffre_affaires_par_categorie(conn) -> list:
    """Chiffre d'affaires total (locations clôturées) groupé par type de véhicule
    (Voiture / Utilitaire / Moto)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT v.type_vehicule AS categorie_vehicule,
               COUNT(l.id_location) AS nb_locations,
               COALESCE(SUM(l.montant_total), 0) AS chiffre_affaires,
               COALESCE(SUM(l.penalite_retard), 0) AS total_penalites
        FROM locations l
        JOIN vehicules v ON v.immatriculation = l.immatriculation
        WHERE l.statut = 'CLOTUREE'
        GROUP BY v.type_vehicule
        ORDER BY chiffre_affaires DESC
    """)
    return cur.fetchall()


def historique_entretien_vehicule(conn, immatriculation: str) -> list:
    """Historique d'entretien complet d'un véhicule donné, du plus récent au plus ancien."""
    cur = conn.cursor()
    cur.execute("""
        SELECT id_entretien, date_entretien, type_entretien, kilometrage, cout, description
        FROM entretiens
        WHERE immatriculation = ?
        ORDER BY date_entretien DESC
    """, (immatriculation,))
    return cur.fetchall()


# ========================================================================
# Fonction utilitaire haut niveau
# ========================================================================
def initialiser_et_synchroniser(flotte: Flotte) -> None:
    with ConnexionDB() as conn:
        creer_tables(conn)
        synchroniser_flotte(conn, flotte)
