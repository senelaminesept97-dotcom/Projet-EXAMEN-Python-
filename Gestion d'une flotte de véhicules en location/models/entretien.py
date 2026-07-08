"""
Classe Entretien : représente une opération de maintenance.

Relation de COMPOSITION : un objet Entretien n'a pas de sens/de cycle de vie
propre en dehors du véhicule qui l'a créé (il est instancié et détruit avec
son véhicule, jamais partagé entre deux véhicules).
"""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Entretien:
    date_entretien: date
    type_entretien: str          # ex: "Vidange", "Révision", "Pneus", "Freins"
    kilometrage: int             # kilométrage du véhicule au moment de l'entretien
    cout: float
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "date_entretien": self.date_entretien.isoformat(),
            "type_entretien": self.type_entretien,
            "kilometrage": self.kilometrage,
            "cout": self.cout,
            "description": self.description,
        }

    @staticmethod
    def from_dict(d: dict) -> "Entretien":
        return Entretien(
            date_entretien=date.fromisoformat(d["date_entretien"]),
            type_entretien=d["type_entretien"],
            kilometrage=int(d["kilometrage"]),
            cout=float(d["cout"]),
            description=d.get("description", ""),
        )

    def __repr__(self) -> str:
        cout_fmt = f"{self.cout:,.0f}".replace(",", " ")
        return (f"<Entretien {self.type_entretien} le {self.date_entretien} "
                f"({self.kilometrage} km, {cout_fmt} FCFA)>")
