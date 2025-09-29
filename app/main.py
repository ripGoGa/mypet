from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

app = FastAPI(title="Bike Tracker")

templates = Jinja2Templates(directory='app/templates')

workouts = [
    {"date": "2025-09-20", "type": "Велотренировка", "duration": 90, "distance": 45},
    {"date": "2025-09-22", "type": "Интервалы", "duration": 60, "distance": 30},
    {"date": "2025-09-24", "type": "Легкая", "duration": 120, "distance": 55},
]


@app.get('/', response_class=HTMLResponse)
async def hello_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'user': 'Спортсмен'})


@app.get('/workouts', response_class=HTMLResponse)
async def list_workouts(request: Request):
    return templates.TemplateResponse('workouts.html', {'request': request, 'workouts': workouts})
