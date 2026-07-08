"""
Gestion de la connexion à la base de données.

Par défaut : SQLite (module standard sqlite3, aucune dépendance externe).
Le projet peut basculer vers MySQL en changeant DB_ENGINE="mysql" dans
config/config.py et en installant le paquet `mysql-connector-python`.
"""
import sqlite3

from config.config import DB_ENGINE, SQLITE_DB_PATH, MYSQL_CONFIG


def get_connection():
    """Retourne une connexion ouverte vers la base configurée."""
    if DB_ENGINE == "sqlite":
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    if DB_ENGINE == "mysql":
        try:
            import mysql.connector
        except ImportError as exc:
            raise ImportError(
                "Le paquet 'mysql-connector-python' est requis pour utiliser MySQL. "
                "Installez-le avec: pip install mysql-connector-python"
            ) from exc
        return mysql.connector.connect(**MYSQL_CONFIG)

    raise ValueError(f"DB_ENGINE inconnu: {DB_ENGINE}")


class ConnexionDB:
    """Context manager pratique : `with ConnexionDB() as conn: ...`"""

    def __enter__(self):
        self.conn = get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
