import datetime
import hashlib

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from pathlib import Path

app = FastAPI(title="Bike Tracker")

templates = Jinja2Templates(directory='app/templates')

workouts = [
    {"date": "2025-09-20", "type": "Велотренировка", "duration": 90, "distance": 45},
    {"date": "2025-09-22", "type": "Интервалы", "duration": 60, "distance": 30},
    {"date": "2025-09-24", "type": "Легкая", "duration": 120, "distance": 55},
]
uploaded_workouts = []


def ensure_data_store():
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
    ct = (file.content_type or '').lower()
    allowed_ct = {'text/csv', 'application/vnd.ms-excel'}
    if not file.filename.lower().endswith('.csv') and ct not in allowed_ct:
        return RedirectResponse(url='/imports?err=type', status_code=303)
    ensure_data_store()
    content = await file.read()
    hash_content = hashlib.sha256(content).hexdigest()
    path = Path('data/csv') / f'{hash_content}.csv'
    if path.exists():
        return RedirectResponse(url='/imports?err=dup', status_code=303)
    path.write_bytes(content)
    uploaded_workouts.append({'hash': hash_content,
                              'original_name': file.filename,
                              'uploaded_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                              })
    return RedirectResponse(url="/imports?ok=1", status_code=303)
