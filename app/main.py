from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

app = FastAPI(title="Bike Tracker")

@app.get('/')
def hello_root():
    return {'message': 'Привет, спортсмен!'}
