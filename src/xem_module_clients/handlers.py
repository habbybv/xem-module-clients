from __future__ import annotations

import json
from datetime import datetime

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse


def build_clients_handlers(deps: dict) -> dict:
    require_any_permission = deps["require_any_permission"]
    require_permission = deps["require_permission"]
    templates = deps["templates"]
    APP_NAME = deps["APP_NAME"]
    has_permission = deps["has_permission"]
    client_crypto_ready = deps["client_crypto_ready"]
    list_clients = deps["list_clients"]
    cached_list_vector_stores = deps["cached_list_vector_stores"]
    sumsub_levels = deps["sumsub_levels"]
    fetch_all = deps["fetch_all"]
    get_client = deps["get_client"]
    get_setting = deps["get_setting"]
    add_months = deps["add_months"]
    parse_date_value = deps["parse_date_value"]
    format_date_value = deps["format_date_value"]
    client_display_name = deps["client_display_name"]
    risk_case_protocol = deps["risk_case_protocol"]
    client_payload_from_form = deps["client_payload_from_form"]
    encrypt_client_payload = deps["encrypt_client_payload"]
    execute = deps["execute"]
    execute_returning_id = deps["execute_returning_id"]
    log_audit = deps["log_audit"]
    kvk_fetch_overview = deps["kvk_fetch_overview"]
    map_overview_to_client_fields = deps["map_overview_to_client_fields"]
    normalize_vat_inputs = deps["normalize_vat_inputs"]
    vies_config = deps["vies_config"]
    vies_auth_headers = deps["vies_auth_headers"]
    httpx = deps["httpx"]
    fetch_one = deps["fetch_one"]
    client_vector_store_id = deps["client_vector_store_id"]
    upload_file = deps["upload_file"]
    attach_file_to_vector_store = deps["attach_file_to_vector_store"]
    create_vector_store_file_batch = deps["create_vector_store_file_batch"]
    OpenAIError = deps["openai_error"]
    format_zentriq_quicknote = deps["format_zentriq_quicknote"]
    zentriq_report_filename = deps["zentriq_report_filename"]
    note_preview = deps["note_preview"]
    read_case_notes = deps["read_case_notes"]
    parse_case_notes = deps["parse_case_notes"]
    parse_note_timestamp = deps["parse_note_timestamp"]
    list_vector_store_files = deps["list_vector_store_files"]
    retrieve_vector_store_file = deps["retrieve_vector_store_file"]
    quote = deps["quote"]
    sumsub_config = deps["sumsub_config"]
    client_default_kyc_level = deps["client_default_kyc_level"]
    sumsub_request = deps["sumsub_request"]
    upsert_sumsub_applicant = deps["upsert_sumsub_applicant"]
    ensure_sumsub_case = deps["ensure_sumsub_case"]
    send_template_email = deps["send_template_email"]
    uuid = deps["uuid"]
    ensure_id_expiry_from_raw = deps["ensure_id_expiry_from_raw"]
    relationship_risk_color = deps["relationship_risk_color"]
    zentriq_select_options = deps["zentriq_select_options"]
    zentriq_finance_fields = deps["zentriq_finance_fields"]
    zentriq_hr_fields = deps["zentriq_hr_fields"]
    zentriq_risk_fields = deps["zentriq_risk_fields"]
    format_zentriq_report = deps["format_zentriq_report"]
    format_zentriq_hr_report = deps["format_zentriq_hr_report"]
    format_zentriq_risk_report = deps["format_zentriq_risk_report"]
    build_zentriq_docx = deps["build_zentriq_docx"]
    require_user = deps["require_user"]
    timezone = deps["timezone"]

    def clients_page(request):
        user = require_any_permission(request, ["client.view", "client.manage"])
        error = None
        clients = []
        if not client_crypto_ready():
            error = "Client encryption key is missing or invalid. Set CLIENT_DATA_KEY to manage clients."
        else:
            clients = list_clients()
        return templates.TemplateResponse(
            "clients.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "message": request.query_params.get("msg"),
                "error": error,
                "clients": clients,
                "can_manage": has_permission(user, "client.manage") or user.get("is_admin"),
            },
        )

    def client_create_page(request, type: str = "BV"):
        user = require_permission(request, "client.manage")
        if not client_crypto_ready():
            error = "Client encryption key is missing or invalid. Set CLIENT_DATA_KEY to manage clients."
            return templates.TemplateResponse(
                "client_form.html",
                {
                    "request": request,
                    "app_name": APP_NAME,
                    "user": user,
                    "message": request.query_params.get("msg"),
                    "error": error,
                    "client": None,
                    "can_manage": True,
                    "is_create": True,
                    "company_type": (type or "BV").upper(),
                    "vector_stores": [],
                    "linked_vector_ids": set(),
                    "assistants": [],
                    "linked_assistant_ids": set(),
                },
            )
        company_type = (type or "BV").upper()
        if company_type not in ("BV", "EZ"):
            company_type = "BV"
        try:
            vector_stores = cached_list_vector_stores()
        except Exception:
            vector_stores = []
        levels = sumsub_levels()
        assistants = fetch_all(
            """
            SELECT name, assistant_id, vector_store_id, model, created_at, is_active
            FROM assistants_registry
            ORDER BY name
            """
        )
        client = {
            "company_type": company_type,
            "status": "Active",
            "risk_level": "Low",
        }
        return templates.TemplateResponse(
            "client_form.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "message": request.query_params.get("msg"),
                "error": None,
                "client": client,
                "can_manage": True,
                "is_create": True,
                "company_type": company_type,
                "auto_fill_open": True,
                "vector_stores": vector_stores,
                "linked_vector_ids": set(),
                "assistants": assistants,
                "linked_assistant_ids": set(),
                "sumsub_levels": levels,
            },
        )

    def client_create_from_kvk(request, kvk: str = "", name: str = ""):
        user = require_permission(request, "client.manage")
        if not client_crypto_ready():
            error = "Client encryption key is missing or invalid. Set CLIENT_DATA_KEY to manage clients."
            return templates.TemplateResponse(
                "client_form.html",
                {
                    "request": request,
                    "app_name": APP_NAME,
                    "user": user,
                    "message": request.query_params.get("msg"),
                    "error": error,
                    "client": None,
                    "can_manage": True,
                    "is_create": True,
                    "company_type": "BV",
                    "vector_stores": [],
                    "linked_vector_ids": set(),
                    "assistants": [],
                    "linked_assistant_ids": set(),
                    "sumsub_levels": [],
                },
            )
        overview, error = kvk_fetch_overview(kvk, name)
        if error or not overview:
            return RedirectResponse("/kvk?msg=KVK%20lookup%20failed", status_code=303)
        fields = map_overview_to_client_fields(overview)
        company_type = (fields.get("company_type") or "BV").upper()
        if company_type not in ("BV", "EZ"):
            company_type = "BV"
        try:
            vector_stores = cached_list_vector_stores()
        except Exception:
            vector_stores = []
        levels = sumsub_levels()
        assistants = fetch_all(
            """
            SELECT name, assistant_id, vector_store_id, model, created_at, is_active
            FROM assistants_registry
            ORDER BY name
            """
        )
        client = {
            "company_type": company_type,
            "status": fields.get("status") or "Active",
            "risk_level": "Low",
            **fields,
        }
        return templates.TemplateResponse(
            "client_form.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "message": request.query_params.get("msg"),
                "error": None,
                "client": client,
                "can_manage": True,
                "is_create": True,
                "company_type": company_type,
                "auto_fill_open": False,
                "vector_stores": vector_stores,
                "linked_vector_ids": set(),
                "assistants": assistants,
                "linked_assistant_ids": set(),
                "sumsub_levels": levels,
            },
        )

    async def clients_create(request):
        user = require_permission(request, "client.manage")
        if not client_crypto_ready():
            return RedirectResponse("/clients?msg=Client%20encryption%20not%20configured", status_code=303)
        form = await request.form()
        payload = client_payload_from_form(form)
        vector_store_id = str(form.get("vector_store_id") or "").strip()
        assistant_id = str(form.get("assistant_id") or "").strip()
        if not payload.get("display_name"):
            return RedirectResponse("/clients?msg=Client%20name%20required", status_code=303)
        now = datetime.utcnow().isoformat()
        enc = encrypt_client_payload(payload)
        client_id = execute_returning_id(
            """
            INSERT INTO clients (created_at, updated_at, created_by, data_enc)
            VALUES (?, ?, ?, ?)
            """,
            (now, now, user["id"], enc),
        )
        if vector_store_id:
            execute(
                "INSERT OR IGNORE INTO client_vector_stores (client_id, vector_store_id) VALUES (?, ?)",
                (client_id, vector_store_id),
            )
        if assistant_id:
            execute(
                "INSERT OR IGNORE INTO client_assistants (client_id, assistant_id) VALUES (?, ?)",
                (client_id, assistant_id),
            )
        log_audit(user["id"], "client.create", f"id={client_id} name={payload.get('display_name')}")
        return RedirectResponse(f"/clients/{client_id}?msg=Client%20created", status_code=303)

    async def clients_lookup(request):
        require_permission(request, "client.manage")
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        name = str(payload.get("name") or "").strip()
        kvk_number = str(payload.get("kvk_number") or "").strip()
        vat_number = str(payload.get("vat_number") or "").strip()

        vat_full = ""
        vies_data = {}
        if vat_number:
            _, _, vat_full = normalize_vat_inputs("", vat_number)
            if vat_full:
                try:
                    _, _, prefix = vies_config()
                    path = f"{prefix}/get/vies/euvat/{vat_full}"
                    url = f"https://viesapi.eu{path}"
                    headers = vies_auth_headers(path)
                    response = httpx.get(url, headers=headers, timeout=20)
                    if response.status_code == 200:
                        vies_data = response.json() or {}
                except Exception:
                    vies_data = {}

        kvk_name = name or vies_data.get("name") or vies_data.get("traderName") or ""
        overview = None
        error = None
        if kvk_number or kvk_name:
            overview, error = kvk_fetch_overview(kvk_number, kvk_name)

        fields = {}
        if overview:
            fields = map_overview_to_client_fields(overview, vat_full or vat_number)
            if not fields.get("display_name") and kvk_name:
                fields["display_name"] = kvk_name
            if not fields.get("statutory_name") and kvk_name:
                fields["statutory_name"] = kvk_name
            if not fields.get("company_address"):
                address = vies_data.get("address") or vies_data.get("traderAddress") or ""
                if isinstance(address, str):
                    fields["company_address"] = address

        if not fields and (vat_full or kvk_number or kvk_name):
            fields = {
                "display_name": kvk_name or "",
                "statutory_name": kvk_name or "",
                "fiscal_number": vat_full or vat_number or "",
            }

        return JSONResponse(
            {
                "ok": bool(fields),
                "fields": fields,
                "error": error,
            }
        )

    def render_client_form(request, user: dict, client_id: int, can_manage: bool):
        error = None
        if not client_crypto_ready():
            error = "Client encryption key is missing or invalid. Set CLIENT_DATA_KEY to manage clients."
            return templates.TemplateResponse(
                "client_form.html",
                {
                    "request": request,
                    "app_name": APP_NAME,
                    "user": user,
                    "message": request.query_params.get("msg"),
                    "error": error,
                    "client": None,
                    "can_manage": False,
                    "vector_stores": [],
                    "assistants": [],
                    "linked_vector_ids": set(),
                    "linked_assistant_ids": set(),
                    "kyc_cases": [],
                    "risk_cases": [],
                    "is_create": False,
                    "company_type": "BV",
                },
            )
        client = get_client(client_id)
        if not client:
            return HTMLResponse("<h3>Client not found.</h3>", status_code=404)
        try:
            vector_stores = cached_list_vector_stores()
        except Exception:
            vector_stores = []
        levels = sumsub_levels()
        assistants = fetch_all(
            """
            SELECT name, assistant_id, vector_store_id, model, created_at, is_active
            FROM assistants_registry
            ORDER BY name
            """
        )
        linked_vectors = fetch_all(
            "SELECT vector_store_id FROM client_vector_stores WHERE client_id = ?",
            (client_id,),
        )
        linked_assistants = fetch_all(
            "SELECT assistant_id FROM client_assistants WHERE client_id = ?",
            (client_id,),
        )
        linked_vector_ids = {row["vector_store_id"] for row in linked_vectors}
        linked_assistant_ids = {row["assistant_id"] for row in linked_assistants}
        kyc_cases = []
        risk_cases = []
        try:
            kyc_cases = fetch_all(
                """
                SELECT c.id as case_id, c.status as case_status, c.created_at, c.updated_at,
                       a.applicant_id, a.external_user_id, a.display_name, a.email, a.review_date,
                       a.review_status, a.review_result
                FROM sumsub_cases c
                LEFT JOIN sumsub_applicants a ON a.applicant_id = c.applicant_id
                WHERE c.client_id = ?
                ORDER BY COALESCE(a.display_name, a.external_user_id, a.applicant_id) ASC
                LIMIT 50
                """,
                (client_id,),
            )
        except Exception as exc:
            error = error or f"Unable to load applicants: {exc}"
        try:
            linked_risk_cases = fetch_all(
                """
                SELECT c.id as case_id,
                       c.status,
                       c.created_at,
                       c.created_at as updated_at,
                       c.priority as overall_risk,
                       c.case_type
                FROM risk_cases c
                WHERE c.client_id = ?
                ORDER BY c.created_at DESC
                LIMIT 50
                """,
                (client_id,),
            )
            linked_invoice_cases = fetch_all(
                """
                SELECT c.id as case_id,
                       c.status,
                       c.protocol_number,
                       c.created_at,
                       c.updated_at,
                       r.overall_risk,
                       'Invoice' as case_type
                FROM risk_invoice_cases c
                LEFT JOIN invoice_reviews r ON r.id = c.invoice_review_id
                WHERE c.client_id = ?
                ORDER BY c.updated_at DESC, c.id DESC
                LIMIT 50
                """,
                (client_id,),
            )
            linked_risk_cases = [dict(row) for row in linked_risk_cases]
            for row in linked_risk_cases:
                row["protocol_number"] = risk_case_protocol(row.get("case_id"), str(row.get("created_at") or ""))
                row["case_url"] = f"/risk/cases/{row.get('case_id')}"
            linked_invoice_cases = [dict(row) for row in linked_invoice_cases]
            for row in linked_invoice_cases:
                row["case_url"] = f"/risk/invoices/{row.get('case_id')}/overview"
            risk_cases = linked_risk_cases + linked_invoice_cases
            risk_cases.sort(key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True)
        except Exception as exc:
            error = error or f"Unable to load risk cases: {exc}"
        return templates.TemplateResponse(
            "client_form.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "message": request.query_params.get("msg"),
                "error": error,
                "client": client,
                "can_manage": can_manage,
                "vector_stores": vector_stores,
                "assistants": assistants,
                "linked_vector_ids": linked_vector_ids,
                "linked_assistant_ids": linked_assistant_ids,
                "kyc_cases": kyc_cases,
                "risk_cases": risk_cases,
                "is_create": False,
                "company_type": (client.get("company_type") or "BV"),
                "sumsub_levels": levels,
            },
        )

    def client_edit(request, client_id: int):
        user = require_permission(request, "client.manage")
        return render_client_form(request, user, client_id, can_manage=True)

    async def client_update(request, client_id: int):
        user = require_permission(request, "client.manage")
        if not client_crypto_ready():
            return RedirectResponse(
                f"/clients/{client_id}?msg=Client%20encryption%20not%20configured",
                status_code=303,
            )
        form = await request.form()
        payload = client_payload_from_form(form)
        vector_store_id = str(form.get("vector_store_id") or "").strip()
        assistant_id = str(form.get("assistant_id") or "").strip()
        if not payload.get("display_name"):
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20name%20required", status_code=303)
        enc = encrypt_client_payload(payload)
        execute(
            "UPDATE clients SET updated_at = ?, data_enc = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), enc, client_id),
        )
        execute("DELETE FROM client_vector_stores WHERE client_id = ?", (client_id,))
        if vector_store_id:
            execute(
                "INSERT OR IGNORE INTO client_vector_stores (client_id, vector_store_id) VALUES (?, ?)",
                (client_id, vector_store_id),
            )
        execute("DELETE FROM client_assistants WHERE client_id = ?", (client_id,))
        if assistant_id:
            execute(
                "INSERT OR IGNORE INTO client_assistants (client_id, assistant_id) VALUES (?, ?)",
                (client_id, assistant_id),
            )
        log_audit(user["id"], "client.update", f"id={client_id}")
        return RedirectResponse(f"/clients/{client_id}?msg=Client%20saved", status_code=303)

    def client_detail(request, client_id: int):
        user = require_any_permission(request, ["client.view", "client.manage"])
        error = None
        if not client_crypto_ready():
            error = "Client encryption key is missing or invalid. Set CLIENT_DATA_KEY to manage clients."
            return templates.TemplateResponse(
                "client_overview.html",
                {
                    "request": request,
                    "app_name": APP_NAME,
                    "user": user,
                    "message": request.query_params.get("msg"),
                    "error": error,
                    "client": None,
                    "assistant": None,
                    "assistant_id": None,
                    "vector_store": None,
                    "kyc_cases": [],
                    "risk_cases": [],
                },
            )
        client = get_client(client_id)
        if not client:
            return HTMLResponse("<h3>Client not found.</h3>", status_code=404)
        refresh_months = int(get_setting("kvk_auto_refresh_months") or 6)
        last_kvk_update = parse_date_value(client.get("kvk_last_update_at") or "")
        kvk_next_refresh_due = ""
        if last_kvk_update:
            kvk_next_refresh_due = format_date_value(add_months(last_kvk_update, refresh_months)) or ""
        linked_vectors = fetch_all(
            "SELECT vector_store_id FROM client_vector_stores WHERE client_id = ?",
            (client_id,),
        )
        linked_assistants = fetch_all(
            "SELECT assistant_id FROM client_assistants WHERE client_id = ?",
            (client_id,),
        )
        vector_store_id = linked_vectors[0]["vector_store_id"] if linked_vectors else None
        assistant_id = linked_assistants[0]["assistant_id"] if linked_assistants else None
        vector_store = None
        assistants = []
        try:
            assistants = fetch_all(
                """
                SELECT name, assistant_id, vector_store_id, model, created_at, is_active
                FROM assistants_registry
                ORDER BY name
                """
            )
        except Exception:
            assistants = []
        if vector_store_id:
            try:
                stores = cached_list_vector_stores()
                vector_store = next((s for s in stores if s["id"] == vector_store_id), None)
            except Exception:
                vector_store = None
        assistant = None
        if assistant_id:
            assistant = next((a for a in assistants if a["assistant_id"] == assistant_id), None)
        kyc_cases = []
        risk_cases = []
        try:
            kyc_cases = fetch_all(
                """
                SELECT c.id as case_id, c.status as case_status, c.created_at, c.updated_at,
                       a.applicant_id, a.external_user_id, a.display_name, a.email, a.review_date, a.raw_json,
                       a.review_status, a.review_result
                FROM sumsub_cases c
                LEFT JOIN sumsub_applicants a ON a.applicant_id = c.applicant_id
                WHERE c.client_id = ?
                ORDER BY COALESCE(a.display_name, a.external_user_id, a.applicant_id) ASC
                LIMIT 50
                """,
                (client_id,),
            )
        except Exception as exc:
            error = error or f"Unable to load applicants: {exc}"
        try:
            linked_risk_cases = fetch_all(
                """
                SELECT c.id as case_id,
                       c.status,
                       c.created_at,
                       c.created_at as updated_at,
                       c.priority as overall_risk,
                       c.case_type
                FROM risk_cases c
                WHERE c.client_id = ?
                ORDER BY c.created_at DESC
                LIMIT 50
                """,
                (client_id,),
            )
            linked_invoice_cases = fetch_all(
                """
                SELECT c.id as case_id,
                       c.status,
                       c.protocol_number,
                       c.created_at,
                       c.updated_at,
                       r.overall_risk,
                       'Invoice' as case_type
                FROM risk_invoice_cases c
                LEFT JOIN invoice_reviews r ON r.id = c.invoice_review_id
                WHERE c.client_id = ?
                ORDER BY c.updated_at DESC, c.id DESC
                LIMIT 50
                """,
                (client_id,),
            )
            linked_risk_cases = [dict(row) for row in linked_risk_cases]
            for row in linked_risk_cases:
                row["protocol_number"] = risk_case_protocol(row.get("case_id"), str(row.get("created_at") or ""))
                row["case_url"] = f"/risk/cases/{row.get('case_id')}"
            linked_invoice_cases = [dict(row) for row in linked_invoice_cases]
            for row in linked_invoice_cases:
                row["case_url"] = f"/risk/invoices/{row.get('case_id')}/overview"
            risk_cases = linked_risk_cases + linked_invoice_cases
            risk_cases.sort(key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True)
        except Exception as exc:
            error = error or f"Unable to load risk cases: {exc}"
        files = fetch_all(
            """
            SELECT id, created_at, file_id, file_name, content_type, size_bytes, source
            FROM client_files
            WHERE client_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (client_id,),
        )
        quicknotes = fetch_all(
            """
            SELECT id, created_at, file_name, note_text
            FROM client_quicknotes
            WHERE client_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (client_id,),
        )
        relationship_links = fetch_all(
            """
            SELECT l.id AS link_id,
                   l.role,
                   l.case_id,
                   c.id AS counterparty_id,
                   c.type,
                   c.name,
                   c.first_name,
                   c.last_name,
                   c.email,
                   c.phone,
                   c.country,
                   c.external_id,
                   sc.case_type,
                   sc.operator_status,
                   sc.applicant_id,
                   sa.id_expiry_date,
                   sa.raw_json
            FROM counterparty_links l
            JOIN counterparties c ON c.id = l.counterparty_id
            LEFT JOIN sumsub_cases sc ON sc.id = l.case_id
            LEFT JOIN sumsub_applicants sa ON sa.applicant_id = sc.applicant_id
            WHERE l.client_id = ?
            ORDER BY l.created_at DESC
            """,
            (client_id,),
        )
        relationship_links = [dict(row) for row in relationship_links]
        for link in relationship_links:
            ensure_id_expiry_from_raw(link)
            state, color = relationship_risk_color(link.get("operator_status"), link.get("id_expiry_date"))
            link["risk_state"] = state
            link["risk_color"] = color
            case_id = link.get("case_id")
            case_type = (link.get("case_type") or "").strip().lower()
            if case_id and case_type:
                link["case_url"] = f"/kyc/case/{case_id}?segment={case_type}"
        return templates.TemplateResponse(
            "client_overview.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "message": request.query_params.get("msg"),
                "error": error,
                "client": client,
                "kvk_next_refresh_due": kvk_next_refresh_due,
                "assistant": assistant,
                "assistant_id": assistant_id,
                "vector_store": vector_store,
                "kyc_cases": kyc_cases,
                "risk_cases": risk_cases,
                "client_files": files,
                "client_quicknotes": quicknotes,
                "client_node": {
                    "id": client_id,
                    "name": client_display_name(client) or f"Client {client_id}",
                },
                "relationship_links": relationship_links,
            },
        )

    async def client_kyc_invite_create(request, client_id: int):
        user = require_any_permission(request, ["client.manage", "kyc.manage"])
        if not client_crypto_ready():
            return JSONResponse({"error": "client_crypto_not_ready"}, status_code=400)
        client = get_client(client_id)
        if not client:
            return JSONResponse({"error": "client_not_found"}, status_code=404)
        form = await request.form()
        full_name = str(form.get("full_name") or "").strip()
        email = str(form.get("email") or "").strip()
        phone = str(form.get("phone") or "").strip()
        send_email_flag = str(form.get("send_email") or "").strip() in {"1", "true", "on", "yes"}
        if not full_name:
            return JSONResponse({"error": "missing_full_name"}, status_code=400)
        if send_email_flag and not email:
            return JSONResponse({"error": "missing_email"}, status_code=400)
        config = sumsub_config()
        if not config.app_token or not config.secret_key:
            return JSONResponse({"error": "sumsub_not_configured"}, status_code=400)
        try:
            level_name = client_default_kyc_level(client_id)
            external_user_id = f"{client_id}-{uuid.uuid4()}"
            payload = {
                "type": "individual",
                "externalUserId": external_user_id,
                "email": email or None,
                "phone": phone or None,
            }
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else "Applicant"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            payload["fixedInfo"] = {
                "firstName": first_name,
                "lastName": last_name or "Applicant",
            }
            response = sumsub_request(
                config,
                "POST",
                "/resources/applicants",
                query={"levelName": level_name},
                body=payload,
            )
            if response.status_code >= 300:
                return JSONResponse({"error": f"sumsub_error_{response.status_code}"}, status_code=400)
            applicant = response.json()
            applicant_id = applicant.get("id", "")
            upsert_sumsub_applicant(applicant)
            ensure_sumsub_case(applicant_id, user["id"], client_id, "KYA", "person")
            token_payload = {
                "applicantIdentifiers": {"email": email or "", "phone": phone or ""},
                "ttlInSecs": 1209600,
                "userId": external_user_id,
                "levelName": level_name,
            }
            token_response = sumsub_request(config, "POST", "/resources/accessTokens/sdk", body=token_payload)
            if token_response.status_code >= 300:
                return JSONResponse({"error": f"sumsub_error_{token_response.status_code}"}, status_code=400)
            data = token_response.json()
            token = data.get("token") or data.get("accessToken")
            email_sent = False
            if send_email_flag and email and token:
                base_url = str(request.base_url).rstrip("/")
                link = f"{base_url}/kyc/start?token={token}"
                client_name = (
                    client.get("display_name")
                    or client.get("statutory_name")
                    or client.get("company_legal_name")
                    or client.get("person_name")
                    or "Client"
                )
                send_template_email(
                    "kyc_invite",
                    email,
                    {
                        "client_name": client_name,
                        "applicant_name": full_name,
                        "link": link,
                    },
                )
                email_sent = True
            return JSONResponse(
                {
                    "token": token,
                    "applicant_id": applicant_id,
                    "email_sent": email_sent,
                }
            )
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=500)

    def client_kvk_refresh(request, client_id: int):
        user = require_permission(request, "client.manage")
        if not client_crypto_ready():
            return JSONResponse({"ok": False, "error": "Client encryption not configured."}, status_code=400)
        client = get_client(client_id)
        if not client:
            return JSONResponse({"ok": False, "error": "Client not found."}, status_code=404)
        kvk_number = client.get("kvk_number") or ""
        name = client.get("statutory_name") or client.get("display_name") or ""
        overview, error = kvk_fetch_overview(kvk_number, name)
        if error or not overview:
            return JSONResponse({"ok": False, "error": error or "KVK lookup failed."}, status_code=400)
        fields = map_overview_to_client_fields(overview)
        if not fields:
            return JSONResponse({"ok": False, "error": "No KVK data returned."}, status_code=400)
        payload = {k: v for k, v in client.items() if k not in {"id", "created_at", "updated_at"}}
        for key, value in fields.items():
            if value:
                payload[key] = value
        now = datetime.utcnow().isoformat()
        payload["kvk_last_update_at"] = now
        enc = encrypt_client_payload(payload)
        execute("UPDATE clients SET updated_at = ?, data_enc = ? WHERE id = ?", (now, enc, client_id))
        log_audit(user["id"], "client.kvk.refresh", f"id={client_id}")
        return JSONResponse({"ok": True, "fields": fields})

    async def client_delete(request, client_id: int):
        user = require_permission(request, "client.manage")
        if not client_crypto_ready():
            return RedirectResponse("/clients?msg=Client%20encryption%20not%20configured", status_code=303)
        row = fetch_one("SELECT id FROM clients WHERE id = ?", (client_id,))
        if not row:
            return RedirectResponse("/clients?msg=Client%20not%20found", status_code=303)
        execute("DELETE FROM client_vector_stores WHERE client_id = ?", (client_id,))
        execute("DELETE FROM client_assistants WHERE client_id = ?", (client_id,))
        execute("DELETE FROM client_files WHERE client_id = ?", (client_id,))
        execute("DELETE FROM client_quicknotes WHERE client_id = ?", (client_id,))
        execute("UPDATE sumsub_cases SET client_id = NULL WHERE client_id = ?", (client_id,))
        execute("UPDATE risk_invoice_cases SET client_id = NULL WHERE client_id = ?", (client_id,))
        execute("DELETE FROM clients WHERE id = ?", (client_id,))
        log_audit(user["id"], "client.delete", f"id={client_id}")
        return RedirectResponse("/clients?msg=Client%20deleted", status_code=303)

    async def client_upload_files(request, client_id: int, files):
        user = require_permission(request, "vector.upload")
        if not client_crypto_ready():
            return RedirectResponse(
                f"/clients/{client_id}?msg=Client%20encryption%20not%20configured",
                status_code=303,
            )
        vector_store_id = client_vector_store_id(client_id)
        if not vector_store_id:
            return RedirectResponse(
                f"/clients/{client_id}?msg=Client%20vector%20not%20linked",
                status_code=303,
            )
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            file_ids = []
            file_meta = []
            for upload in files:
                content = upload.file.read()
                uploaded = upload_file(upload.filename, content, upload.content_type or "")
                file_ids.append(uploaded["id"])
                file_meta.append(
                    (
                        uploaded["id"],
                        upload.filename,
                        upload.content_type or "",
                        len(content),
                    )
                )
            if len(file_ids) == 1:
                attach_file_to_vector_store(vector_store_id, file_ids[0])
            else:
                create_vector_store_file_batch(vector_store_id, file_ids)
            for file_id, filename, ctype, size in file_meta:
                execute(
                    """
                    INSERT INTO client_files
                    (client_id, created_at, uploaded_by, vector_store_id, file_id, file_name, content_type, size_bytes, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (client_id, created_at, user["id"], vector_store_id, file_id, filename, ctype, size, "upload"),
                )
        except OpenAIError as exc:
            return RedirectResponse(f"/clients/{client_id}?msg=Upload%20failed:%20{exc}", status_code=303)
        return RedirectResponse(f"/clients/{client_id}?msg=Files%20uploaded", status_code=303)

    async def client_quicknote(request, client_id: int, quick_note_text: str):
        user = require_permission(request, "report.create.quicknote")
        if not client_crypto_ready():
            return RedirectResponse(
                f"/clients/{client_id}?msg=Client%20encryption%20not%20configured",
                status_code=303,
            )
        vector_store_id = client_vector_store_id(client_id)
        if not vector_store_id:
            return RedirectResponse(
                f"/clients/{client_id}?msg=Client%20vector%20not%20linked",
                status_code=303,
            )
        client = get_client(client_id)
        if not client:
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20missing", status_code=303)
        store_name = ""
        try:
            stores = cached_list_vector_stores()
            for store in stores:
                if store.get("id") == vector_store_id:
                    store_name = store.get("name") or ""
                    break
        except OpenAIError:
            store_name = ""
        data = {
            "operator": user.get("email", ""),
            "quicknote_date": datetime.now(timezone.utc).date().isoformat(),
            "client_name": client_display_name(client),
            "vector_store_id": vector_store_id,
            "quick_note_text": quick_note_text.strip(),
        }
        note_text = format_zentriq_quicknote(data, user_email=user.get("email", ""), store_name=store_name)
        created_at = datetime.now(timezone.utc).isoformat()
        execute(
            """
            INSERT INTO client_quicknotes
            (client_id, created_at, created_by, vector_store_id, file_id, file_name, note_text)
            VALUES (?, ?, ?, ?, NULL, NULL, ?)
            """,
            (client_id, created_at, user["id"], vector_store_id, note_text),
        )
        return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20saved%20(not%20pushed)", status_code=303)

    def client_quicknote_verify(request, client_id: int, note_id: int):
        user = require_permission(request, "report.view")
        row = fetch_one(
            """
            SELECT vector_store_id, file_id
            FROM client_quicknotes
            WHERE id = ? AND client_id = ?
            """,
            (note_id, client_id),
        )
        if not row:
            return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20missing", status_code=303)
        if not row["file_id"]:
            return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20not%20pushed", status_code=303)
        vector_store_id = row["vector_store_id"]
        expected = {row["file_id"]}
        expected = {value for value in expected if value}
        try:
            files = list_vector_store_files(vector_store_id, limit=100).get("data", [])
            present = {f.get("id") or f.get("file_id") for f in files}
            missing = expected - present
            if missing:
                resolved = set()
                for file_id in list(missing):
                    try:
                        retrieve_vector_store_file(vector_store_id, file_id)
                        resolved.add(file_id)
                    except OpenAIError:
                        continue
                missing = missing - resolved
        except OpenAIError as exc:
            return RedirectResponse(f"/clients/{client_id}?msg=Verify%20failed:%20{exc}", status_code=303)
        if missing:
            return RedirectResponse(
                f"/clients/{client_id}?msg=Missing%20files:%20{quote(','.join(sorted(missing)))}",
                status_code=303,
            )
        log_audit(user["id"], "client.quicknote.verify", f"id={note_id} client_id={client_id} ok")
        return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20verified", status_code=303)

    async def client_quicknote_push(request, client_id: int, note_id: int):
        user = require_permission(request, "report.create.quicknote")
        if not client_crypto_ready():
            return RedirectResponse(
                f"/clients/{client_id}?msg=Client%20encryption%20not%20configured",
                status_code=303,
            )
        row = fetch_one(
            """
            SELECT id, created_at, vector_store_id, file_id, note_text
            FROM client_quicknotes
            WHERE id = ? AND client_id = ?
            """,
            (note_id, client_id),
        )
        if not row:
            return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20missing", status_code=303)
        if row["file_id"]:
            return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20already%20pushed", status_code=303)
        vector_store_id = row["vector_store_id"] or client_vector_store_id(client_id)
        if not vector_store_id:
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20vector%20not%20linked", status_code=303)
        client = get_client(client_id)
        if not client:
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20missing", status_code=303)
        created_at = row["created_at"] or datetime.now(timezone.utc).isoformat()
        data = {
            "operator": user.get("email", ""),
            "quicknote_date": created_at[:10],
            "client_name": client_display_name(client),
            "vector_store_id": vector_store_id,
            "quick_note_text": row["note_text"],
        }
        filename = zentriq_report_filename(data, created_at, "txt", "", "quicknote")
        try:
            file_resp = upload_file(filename, (row["note_text"] or "").encode("utf-8"), "text/plain")
            attach_file_to_vector_store(vector_store_id, file_resp["id"])
        except OpenAIError as exc:
            return RedirectResponse(f"/clients/{client_id}?msg=Push%20failed:%20{exc}", status_code=303)
        execute(
            "UPDATE client_quicknotes SET file_id = ?, file_name = ?, vector_store_id = ? WHERE id = ?",
            (file_resp["id"], filename, vector_store_id, note_id),
        )
        log_audit(user["id"], "client.quicknote.push", f"id={note_id} client_id={client_id}")
        return RedirectResponse(f"/clients/{client_id}?msg=Quick%20note%20pushed", status_code=303)

    def client_notes_page(request, client_id: int):
        user = require_any_permission(request, ["client.view", "client.manage"])
        if not client_crypto_ready():
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20encryption%20not%20configured", status_code=303)
        client = get_client(client_id)
        if not client:
            return HTMLResponse("<h3>Client not found.</h3>", status_code=404)
        vector_store_id = client_vector_store_id(client_id)
        user_map = {row["id"]: row["email"] for row in fetch_all("SELECT id, email FROM users")}

        notes = []
        quicknotes = fetch_all(
            """
            SELECT id, created_at, created_by, note_text, file_id
            FROM client_quicknotes
            WHERE client_id = ?
            ORDER BY created_at DESC
            """,
            (client_id,),
        )
        for row in quicknotes:
            author = user_map.get(row["created_by"], "System") if row["created_by"] else "System"
            preview, has_more = note_preview(row["note_text"] or "")
            notes.append(
                {
                    "source": "Client quick note",
                    "source_link": f"/clients/{client_id}",
                    "timestamp": row["created_at"],
                    "author": author,
                    "body": row["note_text"] or "",
                    "preview": preview,
                    "has_more": has_more,
                    "pushed": bool(row["file_id"]),
                    "file_id": row["file_id"],
                    "push_action": f"/clients/{client_id}/quicknote/push",
                    "push_fields": {"note_id": row["id"]},
                    "verify_action": f"/clients/{client_id}/quicknote/verify",
                    "verify_fields": {"note_id": row["id"]},
                }
            )

        risk_cases = fetch_all("SELECT id, case_type FROM risk_cases WHERE client_id = ?", (client_id,))
        invoice_cases = fetch_all("SELECT id, protocol_number FROM risk_invoice_cases WHERE client_id = ?", (client_id,))
        push_rows = fetch_all(
            """
            SELECT case_id, case_kind, note_hash, file_id, created_at
            FROM risk_case_note_pushes
            WHERE case_kind IN ('case','invoice')
            """
        )
        push_map = {}
        for row in push_rows:
            key = (row["case_kind"], row["case_id"], row["note_hash"])
            if key not in push_map:
                push_map[key] = row

        for row in risk_cases:
            notes_text = read_case_notes(row["id"], "case")
            for entry in parse_case_notes(notes_text):
                preview, has_more = note_preview(entry["body"])
                push_key = ("case", row["id"], entry["hash"])
                pushed = push_key in push_map
                file_id = push_map[push_key]["file_id"] if pushed else None
                notes.append(
                    {
                        "source": f"Risk case #{row['id']}",
                        "source_link": f"/risk/cases/{row['id']}/full",
                        "timestamp": entry.get("timestamp", ""),
                        "author": entry.get("author", ""),
                        "body": entry.get("body", ""),
                        "preview": preview,
                        "has_more": has_more,
                        "pushed": pushed,
                        "file_id": file_id,
                        "push_action": f"/risk/cases/{row['id']}/notes/push-one",
                        "push_fields": {
                            "note_timestamp": entry.get("timestamp", ""),
                            "note_author": entry.get("author", ""),
                            "note_body": entry.get("body", ""),
                        },
                        "verify_action": f"/clients/{client_id}/notes/verify",
                        "verify_fields": {"file_id": file_id or ""},
                    }
                )

        for row in invoice_cases:
            notes_text = read_case_notes(row["id"], "invoice")
            for entry in parse_case_notes(notes_text):
                preview, has_more = note_preview(entry["body"])
                push_key = ("invoice", row["id"], entry["hash"])
                pushed = push_key in push_map
                file_id = push_map[push_key]["file_id"] if pushed else None
                notes.append(
                    {
                        "source": f"Invoice case #{row['id']}",
                        "source_link": f"/risk/invoices/{row['id']}",
                        "timestamp": entry.get("timestamp", ""),
                        "author": entry.get("author", ""),
                        "body": entry.get("body", ""),
                        "preview": preview,
                        "has_more": has_more,
                        "pushed": pushed,
                        "file_id": file_id,
                        "push_action": f"/risk/invoices/{row['id']}/notes/push-one",
                        "push_fields": {
                            "note_timestamp": entry.get("timestamp", ""),
                            "note_author": entry.get("author", ""),
                            "note_body": entry.get("body", ""),
                        },
                        "verify_action": f"/clients/{client_id}/notes/verify",
                        "verify_fields": {"file_id": file_id or ""},
                    }
                )

        def _sort_key(item: dict) -> datetime:
            parsed = parse_note_timestamp(item.get("timestamp", ""))
            if parsed:
                return parsed
            try:
                return datetime.fromisoformat(item.get("timestamp", "").replace("Z", "+00:00"))
            except Exception:
                return datetime.min

        notes.sort(key=_sort_key, reverse=True)
        return templates.TemplateResponse(
            "client_notes.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "client": client,
                "client_name": client_display_name(client) or f"Client {client_id}",
                "notes": notes,
                "vector_store_id": vector_store_id,
                "message": request.query_params.get("msg"),
                "return_to": request.query_params.get("return") or f"/clients/{client_id}",
            },
        )

    def client_note_verify(request, client_id: int, file_id: str):
        user = require_permission(request, "report.view")
        vector_store_id = client_vector_store_id(client_id)
        if not vector_store_id:
            return RedirectResponse(f"/clients/{client_id}/notes?msg=Client%20vector%20not%20linked", status_code=303)
        try:
            files = list_vector_store_files(vector_store_id, limit=100).get("data", [])
            present = {f.get("id") or f.get("file_id") for f in files}
            if file_id not in present:
                try:
                    retrieve_vector_store_file(vector_store_id, file_id)
                    return RedirectResponse(f"/clients/{client_id}/notes?msg=Verified", status_code=303)
                except OpenAIError:
                    return RedirectResponse(f"/clients/{client_id}/notes?msg=Missing%20file", status_code=303)
        except OpenAIError as exc:
            return RedirectResponse(f"/clients/{client_id}/notes?msg=Verify%20failed:%20{exc}", status_code=303)
        log_audit(user["id"], "client.note.verify", f"client={client_id} file={file_id}")
        return RedirectResponse(f"/clients/{client_id}/notes?msg=Verified", status_code=303)

    async def client_update_links(request, client_id: int):
        user = require_permission(request, "client.manage")
        form = await request.form()
        vector_store_id = str(form.get("vector_store_id") or "").strip()
        assistant_id = str(form.get("assistant_id") or "").strip()
        execute("DELETE FROM client_vector_stores WHERE client_id = ?", (client_id,))
        if vector_store_id:
            execute(
                "INSERT OR IGNORE INTO client_vector_stores (client_id, vector_store_id) VALUES (?, ?)",
                (client_id, vector_store_id),
            )
        execute("DELETE FROM client_assistants WHERE client_id = ?", (client_id,))
        if assistant_id:
            execute(
                "INSERT OR IGNORE INTO client_assistants (client_id, assistant_id) VALUES (?, ?)",
                (client_id, assistant_id),
            )
        log_audit(
            user["id"],
            "client.links.update",
            f"id={client_id} vectors={'1' if vector_store_id else '0'} assistants={'1' if assistant_id else '0'}",
        )
        return RedirectResponse(f"/clients/{client_id}?msg=Links%20saved", status_code=303)

    def client_report_page(request, client_id: int):
        user = require_permission(request, "report.view")
        if not client_crypto_ready():
            return RedirectResponse("/clients?msg=Client%20encryption%20not%20configured", status_code=303)
        client = get_client(client_id)
        if not client:
            return HTMLResponse("<h3>Client not found.</h3>", status_code=404)
        vector_store_id = client_vector_store_id(client_id)
        if not vector_store_id:
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20vector%20not%20linked", status_code=303)
        stores = []
        store_name = ""
        try:
            stores = cached_list_vector_stores()
            for store in stores:
                if store.get("id") == vector_store_id:
                    store_name = store.get("name") or ""
                    break
        except Exception:
            stores = []
        reports = fetch_all(
            """
            SELECT id, created_at, vector_store_id, file_id, file_name, docx_file_id, docx_file_name, data_json
            FROM zentriq_finance_reports
            WHERE vector_store_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (vector_store_id,),
        )
        parsed = []
        for row in reports:
            try:
                data = json.loads(row["data_json"])
            except Exception:
                data = {}
            parsed.append(
                {
                    "id": row["id"],
                    "created_at": row["created_at"],
                    "vector_store_id": row["vector_store_id"],
                    "file_id": row["file_id"],
                    "file_name": row["file_name"],
                    "docx_file_id": row["docx_file_id"],
                    "docx_file_name": row["docx_file_name"],
                    "client_name": data.get("client_name", ""),
                    "reporting_month": data.get("reporting_month", ""),
                    "report_type": data.get("report_type", "finance"),
                }
            )
        return templates.TemplateResponse(
            "zentriq_finance_report.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "user": user,
                "message": request.query_params.get("msg"),
                "download_report_id": request.query_params.get("download"),
                "select_options": zentriq_select_options,
                "reports": parsed,
                "stores": stores,
                "fixed_vector_store": vector_store_id,
                "fixed_store_name": store_name,
                "fixed_client_name": client_display_name(client),
                "hide_quicknote": True,
                "client_id": client_id,
            },
        )

    async def client_report_submit(request, client_id: int):
        user = require_user(request)
        if not client_crypto_ready():
            return RedirectResponse("/clients?msg=Client%20encryption%20not%20configured", status_code=303)
        client = get_client(client_id)
        if not client:
            return RedirectResponse("/clients?msg=Client%20not%20found", status_code=303)
        vector_store_id = client_vector_store_id(client_id)
        if not vector_store_id:
            return RedirectResponse(f"/clients/{client_id}?msg=Client%20vector%20not%20linked", status_code=303)
        form = await request.form()
        report_type = str(form.get("report_type", "finance")).strip().lower()
        if report_type not in ("finance", "hr", "risk"):
            report_type = "finance"
        data = {}
        if report_type == "finance":
            fields = zentriq_finance_fields
        elif report_type == "hr":
            fields = zentriq_hr_fields
        else:
            fields = zentriq_risk_fields
        for key in fields:
            if key in form:
                value = str(form.get(key)).strip()
                data[key] = value
        data["operator"] = user.get("email", "")
        data["report_type"] = report_type
        data["vector_store_id"] = vector_store_id
        store_name = ""
        try:
            stores = cached_list_vector_stores()
            for store in stores:
                if store.get("id") == vector_store_id:
                    store_name = store.get("name") or ""
                    break
        except OpenAIError:
            store_name = ""
        if store_name:
            if report_type == "risk":
                data["company_name"] = client_display_name(client) or store_name
            else:
                data["client_name"] = client_display_name(client) or store_name
        created_at = datetime.now(timezone.utc).isoformat()
        if report_type == "finance":
            if not has_permission(user, "report.create.finance"):
                return RedirectResponse(f"/clients/{client_id}/reports/new?msg=Access%20denied", status_code=303)
            report_text = format_zentriq_report(data, user_email=user.get("email", ""), store_name=store_name)
            prefix = "financial_report"
        elif report_type == "hr":
            if not has_permission(user, "report.create.hr"):
                return RedirectResponse(f"/clients/{client_id}/reports/new?msg=Access%20denied", status_code=303)
            report_text = format_zentriq_hr_report(data, user_email=user.get("email", ""), store_name=store_name)
            prefix = "hr_report"
        else:
            if not has_permission(user, "report.create.risk"):
                return RedirectResponse(f"/clients/{client_id}/reports/new?msg=Access%20denied", status_code=303)
            report_text = format_zentriq_risk_report(data, user_email=user.get("email", ""), store_name=store_name)
            prefix = "risk_report"
        txt_filename = zentriq_report_filename(data, created_at, "txt", store_name, prefix)
        docx_filename = zentriq_report_filename(data, created_at, "docx", store_name, prefix)
        docx_bytes = build_zentriq_docx(report_text)
        try:
            file_resp = upload_file(txt_filename, report_text.encode("utf-8"), "text/plain")
            attach_file_to_vector_store(vector_store_id, file_resp["id"])
        except OpenAIError as exc:
            return RedirectResponse(f"/clients/{client_id}/reports/new?msg=Upload%20failed:%20{exc}", status_code=303)
        report_id = execute_returning_id(
            """
            INSERT INTO zentriq_finance_reports
            (user_id, created_at, vector_store_id, file_id, file_name, docx_file_id, docx_file_name, report_text, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                created_at,
                vector_store_id,
                file_resp["id"],
                txt_filename,
                "",
                docx_filename,
                report_text,
                json.dumps(data),
            ),
        )
        return RedirectResponse(
            f"/clients/{client_id}/reports/new?msg=Report%20saved&download={report_id}",
            status_code=303,
        )

    return {
        "clients_page": clients_page,
        "client_create_page": client_create_page,
        "client_create_from_kvk": client_create_from_kvk,
        "clients_create": clients_create,
        "clients_lookup": clients_lookup,
        "render_client_form": render_client_form,
        "client_edit": client_edit,
        "client_update": client_update,
        "client_detail": client_detail,
        "client_kyc_invite_create": client_kyc_invite_create,
        "client_kvk_refresh": client_kvk_refresh,
        "client_delete": client_delete,
        "client_upload_files": client_upload_files,
        "client_quicknote": client_quicknote,
        "client_quicknote_verify": client_quicknote_verify,
        "client_quicknote_push": client_quicknote_push,
        "client_notes_page": client_notes_page,
        "client_note_verify": client_note_verify,
        "client_update_links": client_update_links,
        "client_report_page": client_report_page,
        "client_report_submit": client_report_submit,
    }
