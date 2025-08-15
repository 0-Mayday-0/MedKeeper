from decimal import Decimal
from decimal import getcontext

class Medication:
    def __init__(self, name: str, strength: float | int, qty: float | int, ndecimals: int = 2) -> None:
        getcontext().prec = int(ndecimals)
        self.ndecimals: int = ndecimals
        self.name: str = name
        self.strength: Decimal = Decimal(strength)
        self.qty: Decimal = Decimal(qty)

    def __repr__(self) -> str:
        return f'Med({self.name=}, {self.strength=}, {self.qty=})'

    def __dict__(self) -> dict:
        return {'name': self.name,
                'strength': round(float(self.strength), self.ndecimals),
                'qty': round(float(self.qty), self.ndecimals)}

    @property
    def get_name(self) -> str:
        return self.name

    @property
    def get_strength(self) -> Decimal:
        return Decimal(self.strength)

    @property
    def get_qty(self) -> Decimal:
        return Decimal(self.qty)

def main() -> None:
    vila = Medication(name="Vilazodone", strength=40, qty=30.5)

    print(vila.get_name)
    print(vila.get_strength)
    print(vila.get_qty)

if __name__ == "__main__":
    main()