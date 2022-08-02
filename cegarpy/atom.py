from pydantic.dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Atom:
    symbol: str

    def __str__(self) -> str:
        return self.symbol
