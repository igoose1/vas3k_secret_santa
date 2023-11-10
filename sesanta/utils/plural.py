# ruff: noqa: PLR2004


class RuPlural:
    def __init__(self, odna: str, dve: str, vosem: str):
        self.korova = odna
        self.korovy = dve
        self.korov = vosem

    def __call__(self, number: int) -> str:
        if number % 10 == 1 and number != 11:
            return self.korova
        if 2 <= number % 10 <= 4 and number // 10 != 1:
            return self.korovy
        return self.korov
