from math import ceil
from typing import Optional

from app.services.ai_coach import get_ollama_service, OllamaService
from app.services.file_service import (
    validate_file_type,
    save_file_with_hash,
    FileValidationError,
    FileAlreadyExistsError
)
from app.db import create_db_and_tables, get_session
from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.models import UploadedFile, Workout, UserProfile, ChatMessage
from starlette.requests import Request
from pathlib import Path
from sqlmodel import Session, select
from datetime import datetime, UTC, date
from sqlalchemy import desc, func

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
async def list_workouts(request: Request, session: Session = Depends(get_session), page: int = 1):
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    total_count = session.exec(select(func.count(Workout.id))).one()
    total_pages = ceil(total_count / limit)
    workouts = session.exec(select(Workout).order_by(desc(Workout.id)).limit(limit).offset(offset)).all()
    return templates.TemplateResponse('workouts.html', {'request': request, 'workouts': workouts,
                                                        'current_page': page,
                                                        'total_pages': total_pages})


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


@app.get('/profile', response_class=HTMLResponse)
async def show_profile(request: Request, session: Session = Depends(get_session)):
    profile = session.exec(select(UserProfile)).first()
    if profile is None:
        return RedirectResponse(url='/profile/create', status_code=303)
    return templates.TemplateResponse('profile.html', {'request': request, 'profile': profile})


@app.get('/profile/create', response_class=HTMLResponse)
async def check_created_profile(request: Request, session: Session = Depends(get_session)):
    profile = session.exec(select(UserProfile)).first()
    if profile is None:
        return templates.TemplateResponse('profile_create.html', {'request': request})
    return RedirectResponse(url='/profile', status_code=303)


@app.post("/profile/create", response_class=HTMLResponse)
async def create_profile(
        name: str = Form(...),
        weight_kg: float = Form(...),
        ftp: int = Form(...),
        birth_date: Optional[date] = Form(None),
        height_cm: Optional[int] = Form(None),
        session: Session = Depends(get_session)
):
    if session.exec(select(UserProfile)).first() is None:
        user_profile = UserProfile(name=name, weight_kg=weight_kg, birth_date=birth_date, height_cm=height_cm,
                                   ftp=ftp)
        session.add(user_profile)
        session.commit()
    return RedirectResponse(url='/profile', status_code=303)


@app.get('/profile/edit', response_class=HTMLResponse)
async def check_edited_profile(request: Request, session: Session = Depends(get_session)):
    profile = session.exec(select(UserProfile)).first()
    if profile is not None:
        return templates.TemplateResponse('profile_edit.html', {'request': request, 'profile': profile})
    return RedirectResponse(url='/profile/create', status_code=303)


@app.post('/profile/edit', response_class=HTMLResponse)
async def edit_profile(
        name: str = Form(...),
        weight_kg: float = Form(...),
        ftp: int = Form(...),
        birth_date: Optional[date] = Form(None),
        height_cm: Optional[int] = Form(None),
        session: Session = Depends(get_session)
):
    profile = session.exec(select(UserProfile)).first()
    profile.name = name
    profile.weight_kg = weight_kg
    profile.height_cm = height_cm
    profile.ftp = ftp
    profile.birth_date = birth_date
    profile.updated_at = datetime.now()
    session.commit()
    return RedirectResponse(url='/profile', status_code=303)


@app.get('/workouts/{workout_id}', response_class=HTMLResponse)
async def workout_detail(workout_id: int, request: Request, session: Session = Depends(get_session)):
    workout = session.exec(select(Workout).where(Workout.id == workout_id)).first()
    if not workout:
        raise HTTPException(status_code=404, detail='Тренировка не найдена')
    return templates.TemplateResponse('workout_detail.html', {'request': request, 'workout': workout})


@app.get('/coach', response_class=HTMLResponse)
async def coach_page(request: Request, session: Session = Depends(get_session)):
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    message_history = session.exec(select(ChatMessage).where(profile.id == ChatMessage.user_id).order_by(
        ChatMessage.created_at)).all()

    return templates.TemplateResponse('coach.html', {'request': request, 'message_history': message_history})


@app.post('/coach/advice', response_class=HTMLResponse)
async def get_advice(request: Request, session: Session = Depends(get_session), num_workouts: int = Form(5),
                     ollama_service: OllamaService = Depends(get_ollama_service)):
    workouts = session.exec(select(Workout).order_by(desc(Workout.id)).limit(num_workouts)).all()
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    advice = await ollama_service.get_training_advice(profile, workouts)
    return templates.TemplateResponse('advice.html', {'request': request, 'advice': advice})


@app.post('/coach/chat', response_class=HTMLResponse)
async def chat(request: Request, user_question: str = Form(...), session: Session = Depends(get_session),
               ollama_service=Depends(get_ollama_service)):
    # Получаем данные
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    workouts = session.exec(select(Workout).order_by(desc(Workout.id)).limit(10)).all()
    message_history = session.exec(select(ChatMessage).where(profile.id == ChatMessage.user_id).order_by(
        ChatMessage.created_at)).all()
    # Сохраняем вопрос пользователя
    user_message = ChatMessage(user_id=profile.id, role='user', content=user_question)
    session.add(user_message)
    session.commit()
    # Вызываем ИИ и передаем старую историю + новый вопрос
    answer = await ollama_service.get_chat_response(profile=profile, workouts=workouts, history=message_history,
                                                    user_question=user_question)
    # Сохраняем новый ответ в контекст
    assistant_message = ChatMessage(user_id=profile.id, role='assistant', content=answer)
    session.add(assistant_message)
    session.commit()

    return RedirectResponse(url='/coach', status_code=303)