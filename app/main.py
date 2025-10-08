import datetime
import hashlib
from app.services.file_service import (
    validate_file_type,
    save_file_with_hash,
    FileValidationError,
    FileAlreadyExistsError
)
from app.db import create_db_and_tables, get_session
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from pathlib import Path

app = FastAPI(title="Bike Tracker")

templates = Jinja2Templates(directory='app/templates')


def on_startup() -> None:
    create_db_and_tables()


workouts = [
    {"date": "2025-09-20", "type": "Велотренировка", "duration": 90, "distance": 45},
    {"date": "2025-09-22", "type": "Интервалы", "duration": 60, "distance": 30},
    {"date": "2025-09-24", "type": "Легкая", "duration": 120, "distance": 55},
]
uploaded_workouts = []


def ensure_data_store() -> None:
    Path('data/csv').mkdir(parents=True, exist_ok=True)


@app.get('/', response_class=HTMLResponse)
async def hello_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'user': 'Спортсмен'})


@app.get('/workouts', response_class=HTMLResponse)
async def list_workouts(request: Request):
    return templates.TemplateResponse('workouts.html', {'request': request,
                                                        'workouts': workouts,
                                                        'uploaded_workouts': uploaded_workouts})


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
async def import_csv(file: UploadFile = File(...)):
    try:
        validate_file_type(filename=file.filename, content_type=file.content_type)
        content = await file.read()
        file_path = save_file_with_hash(content)
        return RedirectResponse(url='/imports?ok=1', status_code=303)

    except FileValidationError:
        return RedirectResponse(url='/imports?err=type', status_code=303)
    except FileAlreadyExistsError:
        return RedirectResponse(url='/imports?err=dup', status_code=303)
    except OSError:
        return RedirectResponse(url='/imports?err=write', status_code=303)
