from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse


def create_router(deps: dict) -> APIRouter:
    clients_page_handler = deps["clients_page_handler"]
    client_create_page_handler = deps["client_create_page_handler"]
    client_create_from_kvk_handler = deps["client_create_from_kvk_handler"]
    clients_create_handler = deps["clients_create_handler"]
    clients_lookup_handler = deps["clients_lookup_handler"]
    client_detail_handler = deps["client_detail_handler"]
    client_kyc_invite_create_handler = deps["client_kyc_invite_create_handler"]
    client_edit_handler = deps["client_edit_handler"]
    client_update_handler = deps["client_update_handler"]
    client_kvk_refresh_handler = deps["client_kvk_refresh_handler"]
    client_delete_handler = deps["client_delete_handler"]
    client_upload_files_handler = deps["client_upload_files_handler"]
    client_quicknote_handler = deps["client_quicknote_handler"]
    client_quicknote_verify_handler = deps["client_quicknote_verify_handler"]
    client_quicknote_push_handler = deps["client_quicknote_push_handler"]
    client_notes_page_handler = deps["client_notes_page_handler"]
    client_note_verify_handler = deps["client_note_verify_handler"]
    client_update_links_handler = deps["client_update_links_handler"]
    client_report_page_handler = deps["client_report_page_handler"]
    client_report_submit_handler = deps["client_report_submit_handler"]

    router = APIRouter()

    @router.get("/clients/health", name="clients_health")
    def clients_health() -> dict[str, str]:
        return {"status": "ok", "module": "clients"}

    @router.get("/clients", response_class=HTMLResponse)
    def clients_page(request: Request):
        return clients_page_handler(request)

    @router.get("/clients/new", response_class=HTMLResponse)
    def client_create_page(request: Request, type: str = "BV"):
        return client_create_page_handler(request, type)

    @router.get("/clients/new/from-kvk", response_class=HTMLResponse)
    def client_create_from_kvk(request: Request, kvk: str = "", name: str = ""):
        return client_create_from_kvk_handler(request, kvk, name)

    @router.post("/clients")
    async def clients_create(request: Request):
        return await clients_create_handler(request)

    @router.post("/clients/lookup", response_class=JSONResponse)
    async def clients_lookup(request: Request):
        return await clients_lookup_handler(request)

    @router.get("/clients/{client_id}", response_class=HTMLResponse)
    def client_detail(request: Request, client_id: int):
        return client_detail_handler(request, client_id)

    @router.post("/clients/{client_id}/kyc-invite-create", response_class=JSONResponse)
    async def client_kyc_invite_create(request: Request, client_id: int):
        return await client_kyc_invite_create_handler(request, client_id)

    @router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
    def client_edit(request: Request, client_id: int):
        return client_edit_handler(request, client_id)

    @router.post("/clients/{client_id}/update")
    async def client_update(request: Request, client_id: int):
        return await client_update_handler(request, client_id)

    @router.post("/clients/{client_id}/kvk-refresh", response_class=JSONResponse)
    def client_kvk_refresh(request: Request, client_id: int):
        return client_kvk_refresh_handler(request, client_id)

    @router.post("/clients/{client_id}/delete")
    async def client_delete(request: Request, client_id: int):
        return await client_delete_handler(request, client_id)

    @router.post("/clients/{client_id}/files")
    async def client_upload_files(request: Request, client_id: int, files: list[UploadFile] = File(...)):
        return await client_upload_files_handler(request, client_id, files)

    @router.post("/clients/{client_id}/quicknote")
    async def client_quicknote(request: Request, client_id: int, quick_note_text: str = Form(...)):
        return await client_quicknote_handler(request, client_id, quick_note_text)

    @router.post("/clients/{client_id}/quicknote/verify")
    def client_quicknote_verify(request: Request, client_id: int, note_id: int = Form(...)):
        return client_quicknote_verify_handler(request, client_id, note_id)

    @router.post("/clients/{client_id}/quicknote/push")
    async def client_quicknote_push(request: Request, client_id: int, note_id: int = Form(...)):
        return await client_quicknote_push_handler(request, client_id, note_id)

    @router.get("/clients/{client_id}/notes", response_class=HTMLResponse)
    def client_notes_page(request: Request, client_id: int):
        return client_notes_page_handler(request, client_id)

    @router.post("/clients/{client_id}/notes/verify")
    def client_note_verify(request: Request, client_id: int, file_id: str = Form(...)):
        return client_note_verify_handler(request, client_id, file_id)

    @router.post("/clients/{client_id}/links")
    async def client_update_links(request: Request, client_id: int):
        return await client_update_links_handler(request, client_id)

    @router.get("/clients/{client_id}/reports/new", response_class=HTMLResponse)
    def client_report_page(request: Request, client_id: int):
        return client_report_page_handler(request, client_id)

    @router.post("/clients/{client_id}/reports")
    async def client_report_submit(request: Request, client_id: int):
        return await client_report_submit_handler(request, client_id)

    return router
