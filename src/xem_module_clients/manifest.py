from __future__ import annotations

from typing import Any


def get_manifest() -> dict[str, Any]:
    return {
        "id": "clients",
        "name": "Clients",
        "version": "0.1.0",
        "description": "Client pages and workflows",
        "category": "operations",
        "enabled_by_default": True,
        "entry": {
            "router": "xem_module_clients.routes:create_router",
            "mount_prefix": "",
        },
        "dashboard": {
            "label": "Clients",
            "href": "/clients",
            "icon": "👥",
        },
        "compat": {
            "core_api": ">=1.0.0,<2.0.0",
        },
        "permissions": {
            "required": ["clients.view"],
            "admin": ["clients.manage"],
        },
        "nav_items": [
            {"label": "Clients", "href": "/clients", "order": 40, "scope": "main"},
        ],
        "client_scope": {"enabled": False},
        "migrations": {"path": "migrations"},
        "health": {"path": "/clients/health"},
    }

