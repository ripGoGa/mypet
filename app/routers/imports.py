from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_current_user, get_import_service
from app.core.templating import templates
from app.db.session import get_session
from app.models.models import Users
from app.services.import_service import ImportService

router = APIRouter()


@router.get('/imports')
def imports(request: Request, user: Users = Depends(get_current_user)):
    success_count = int(request.query_params.get('success')) if request.query_params.get('success') else 0
    dup_count = int(request.query_params.get('dup')) if request.query_params.get('dup') else 0
    err_count = int(request.query_params.get('err')) if request.query_params.get('err') else 0
    message = None
    if 'success' in request.query_params or 'dup' in request.query_params or 'err' in request.query_params:
        message = f'Успешно загружено: {success_count}, Пропущено дубликатов: {dup_count}, Ошибок: {err_count}'
    return templates.TemplateResponse(request, 'imports.html', {'message': message})


@router.post('/imports')
async def imports_file(files: list[UploadFile] = File(...), service: ImportService = Depends(get_import_service),
                       user: Users = Depends(get_current_user)):
    if not user.user_profile:
        return RedirectResponse(url='/profile/create', status_code=303)
    success_count, dup_count, type_err_count = await service.import_files(files=files, user=user)
    return RedirectResponse(url=f'/imports?success={success_count}&dup={dup_count}&err={type_err_count}',
                            status_code=303)
