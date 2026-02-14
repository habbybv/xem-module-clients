from importlib.metadata import entry_points


def test_xem_modules_entrypoint_declared() -> None:
    eps = entry_points()
    try:
        group = eps.select(group="xem.modules")
    except Exception:
        group = eps.get("xem.modules", [])
    names = {str(ep.name) for ep in group}
    expected = "clients"
    assert expected in names
