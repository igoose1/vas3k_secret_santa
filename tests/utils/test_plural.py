from sesanta.utils.plural import RuPlural


def test_ruplural() -> None:
    rp = RuPlural("корова", "коровы", "коров")
    assert rp(1) == "корова"
    assert rp(2) == "коровы"
    assert rp(8) == "коров"
