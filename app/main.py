from app.services.file_service import (
    validate_file_type,
    save_file_with_hash,
    FileValidationError,
    FileAlreadyExistsError
)
from app.db import create_db_and_tables, get_session
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.models import UploadedFile, Workout
from starlette.requests import Request
from pathlib import Path
from sqlmodel import Session, select
from datetime import datetime, UTC
from sqlalchemy import desc

from app.services.parse_cvs import parse_csv_to_workout, ParseCsvError

app = FastAPI(title="Bike Tracker")

templates = Jinja2Templates(directory='app/templates')


def on_startup() -> None:
    create_db_and_tables()


on_startup()


def ensure_data_store() -> None:
    Path('data/csv').mkdir(parents=True, exist_ok=True)


@app.get('/', response_class=HTMLResponse)
async def hello_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'user': 'Спортсмен'})


@app.get('/workouts', response_class=HTMLResponse)
async def list_workouts(request: Request, session: Session = Depends(get_session)):
    workouts = session.exec(select(Workout)).all()
    last_3_uploaded = session.exec(select(UploadedFile).order_by(desc(UploadedFile.uploaded_at)).limit(3)).all()
    return templates.TemplateResponse('workouts.html', {'request': request,
                                                        'workouts': workouts,
                                                        'last_3_uploaded': last_3_uploaded})


@app.get('/imports', response_class=HTMLResponse)
async def imports(request: Request):
    ok = request.query_params.get('ok')
    err = request.query_params.get('err')

    message = None
    is_error = False
    if ok == '1':
        message = 'Файл успешно сохранен'
    elif err == 'dup':
        message = 'Такой файл уже импортирован'
        is_error = True
    elif err == 'type':
        message = 'Можно загружать только CSV-файлы!'
        is_error = True

    return templates.TemplateResponse('imports.html', {'request': request, 'message': message, 'is_error': is_error})


@app.post('/imports')
async def import_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    try:
        validate_file_type(filename=file.filename, content_type=file.content_type)
        content = await file.read()
        file_path, hash_value = save_file_with_hash(content, session)
        uploaded_file = UploadedFile(original_name=file.filename, sha256=hash_value, uploaded_at=datetime.now(UTC))
        session.add(uploaded_file)
        session.flush()

        parse_csv_to_workout(file_path=file_path, uf_id=uploaded_file.id, session=session)
        session.commit()
        return RedirectResponse(url='/imports?ok=1', status_code=303)
    except ParseCsvError:
        session.rollback()
        return RedirectResponse(url='/imports?err=parse', status_code=303)
    except FileValidationError:
        session.rollback()
        return RedirectResponse(url='/imports?err=type', status_code=303)
    except FileAlreadyExistsError:
        session.rollback()
        return RedirectResponse(url='/imports?err=dup', status_code=303)
    except OSError:
        session.rollback()
        return RedirectResponse(url='/imports?err=write', status_code=303)
