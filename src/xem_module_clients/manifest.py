from __future__ import annotations

from typing import Any


def get_manifest() -> dict[str, Any]:
    return {
        "id": "clients",
        "name": "Clients",
        "version": "0.1.3",
        "description": "Client registry, profiles, and report workflows",
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
        "contract": {
            "required_deps": [
                "client_autoscore_run_detail_handler",
                "client_create_from_kvk_handler",
                "client_create_page_handler",
                "client_delete_handler",
                "client_detail_handler",
                "client_edit_handler",
                "client_kvk_refresh_handler",
                "client_kyc_invite_create_handler",
                "client_note_verify_handler",
                "client_notes_page_handler",
                "client_quicknote_handler",
                "client_quicknote_push_handler",
                "client_quicknote_verify_handler",
                "client_report_page_handler",
                "client_report_submit_handler",
                "client_update_handler",
                "client_update_links_handler",
                "client_upload_files_handler",
                "clients_create_handler",
                "clients_lookup_handler",
                "clients_page_handler",
            ]
        },
        "permissions": {
            "required": ["client.view"],
            "admin": ["client.manage"],
        },
        "nav_items": [
            {"label": "Clients", "href": "/clients", "order": 25, "scope": "main"},
        ],
        "client_scope": {"enabled": False},
        "migrations": {"path": "migrations"},
        "health": {"path": "/clients/health"},
    }
