from importlib import import_module

from xem_module_clients.manifest import get_manifest


def test_manifest_has_required_shape() -> None:
    manifest = get_manifest()
    assert manifest["entry"]["router"].startswith("xem_module_clients.routes:")
    assert "id" in manifest and manifest["id"]


def test_router_entrypoint_resolves_callable() -> None:
    router_entry = get_manifest()["entry"]["router"]
    module_name, func_name = router_entry.split(":", 1)
    module = import_module(module_name)
    assert callable(getattr(module, func_name))
