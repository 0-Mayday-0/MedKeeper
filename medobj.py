from decimal import Decimal
from decimal import getcontext
from bson.objectid import ObjectId
import strings as s

class Medication:
    def __init__(self, objid: None | ObjectId, name: str, strength: float | int, qty: float | int,
                 ndecimals: int = 2) -> None:
        getcontext().prec = int(ndecimals)
        self.ndecimals: int = ndecimals
        self.name: str = name
        self.strength: Decimal = Decimal(strength)
        self.qty: Decimal = Decimal(qty)
        self.id: None | ObjectId = objid

    def __repr__(self) -> str:
        return f'Med({self.id=}, {self.name=}, {self.strength=}, {self.qty=})'

    def __str__(self) -> str:
        return f'{self.name}: {self.strength}{s.Menu.External.milligrams} {s.Menu.External.stock}{self.qty}'

    def __dict__(self) -> dict:
        return {s.Connections.name_str: self.name,
                s.Connections.strength_str: round(float(self.strength), self.ndecimals),
                s.Connections.qty_str: round(float(self.qty), self.ndecimals)}

    @property
    def get_name(self) -> str:
        return self.name

    @property
    def get_strength(self) -> Decimal:
        return Decimal(self.strength)

    @property
    def get_qty(self) -> Decimal:
        return Decimal(self.qty)

    @property
    def get_id(self) -> ObjectId | None:
        return self.id

def main() -> None:
    vila = Medication(name="Vilazodone", strength=40, qty=30.5)

    print(vila.get_name)
    print(vila.get_strength)
    print(vila.get_qty)

if __name__ == "__main__":
    main()