"""
Fonctions utilitaires génériques utilisées par plusieurs modules.
"""
from datetime import date, datetime


def parser_date(texte: str) -> date:
    """Convertit une chaîne 'YYYY-MM-DD' en objet date. Lève ValueError sinon."""
    return datetime.strptime(texte, "%Y-%m-%d").date()


def formater_montant(montant: float) -> str:
    """Formate un montant en Francs CFA (XOF). Le FCFA n'a pas de sous-unité
    d'usage courant : on affiche un entier avec séparateur de milliers."""
    return f"{round(montant):,} FCFA".replace(",", " ")


def formater_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def afficher_titre(titre: str, largeur: int = 70) -> None:
    print("\n" + "=" * largeur)
    print(titre.center(largeur))
    print("=" * largeur)


def afficher_tableau(lignes: list, entetes: list) -> None:
    """Affiche un tableau texte simple, aligné automatiquement, dans la console."""
    lignes_str = [[str(cell) for cell in ligne] for ligne in lignes]
    largeurs = [len(h) for h in entetes]
    for ligne in lignes_str:
        for i, cell in enumerate(ligne):
            largeurs[i] = max(largeurs[i], len(cell))

    def fmt_ligne(cells):
        return " | ".join(c.ljust(largeurs[i]) for i, c in enumerate(cells))

    print(fmt_ligne(entetes))
    print("-+-".join("-" * l for l in largeurs))
    for ligne in lignes_str:
        print(fmt_ligne(ligne))
