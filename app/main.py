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
from app.models.models import UploadedFile, Workout, UserProfile, ChatMessage, AthleteProfile
from starlette.requests import Request
from pathlib import Path
from sqlmodel import Session, select
from datetime import datetime, UTC, date, timedelta
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
async def hello_root(request: Request, session: Session = Depends(get_session)):
    # Пытаемся узнать имя пользователя для приветствия
    user = session.exec(select(UserProfile)).first()

    return templates.TemplateResponse('index.html', {'request': request, 'user_profile': user})


@app.get('/workouts', response_class=HTMLResponse)
async def list_workouts(request: Request, session: Session = Depends(get_session), page: int = 1, period: int = 0,
                        limit: int = 10):
    if page < 1:
        page = 1
    if limit > 100 or limit < 1:
        limit = 10
    offset = (page - 1) * limit

    # 1. Чистый запрос
    query_workouts = select(Workout)
    query_count = select(func.count(Workout.id))

    # 2. Формируем запрос из роута статистики
    if period:
        target_date = datetime.now() - timedelta(days=period)
        query_workouts = query_workouts.join(UploadedFile).where(UploadedFile.uploaded_at >= target_date)
        query_count = query_count.join(UploadedFile).where(UploadedFile.uploaded_at >= target_date)

    # 3. Формируем запрос для простого просмотра тренировок
    query_workouts = query_workouts.order_by(desc(Workout.id)).limit(limit).offset(offset)

    # 4. Делаем запрос в базу
    workouts = session.exec(query_workouts).all()
    total_count = session.exec(query_count).one()
    total_pages = ceil(total_count / limit)

    return templates.TemplateResponse('workouts.html', {'request': request, 'workouts': workouts,
                                                        'current_page': page,
                                                        'total_pages': total_pages, 'period': period,
                                                        'limit': limit})


@app.get('/imports', response_class=HTMLResponse)
async def imports(request: Request):
    success_count = int(request.query_params.get('success')) if request.query_params.get('success') else 0
    dup_count = int(request.query_params.get('dup')) if request.query_params.get('dup') else 0
    err_count = int(request.query_params.get('err')) if request.query_params.get('err') else 0
    message = None
    if 'success' in request.query_params or 'dup' in request.query_params or 'err' in request.query_params:
        message = f'Успешно загружено: {success_count}, Пропущено дубликатов: {dup_count}, Ошибок: {err_count}'
    return templates.TemplateResponse('imports.html', {'request': request, 'message': message})


@app.post('/imports')
async def import_csv(files: list[UploadFile] = File(...), session: Session = Depends(get_session)):
    user = session.exec(select(UserProfile)).first()
    success_count = 0
    dup_count = 0
    type_err_count = 0

    if not user:
        return RedirectResponse(url='/profile/create', status_code=303)
    for file in files:
        try:
            validate_file_type(filename=file.filename, content_type=file.content_type)
            content = await file.read()
            file_path, hash_value = save_file_with_hash(content, session)
            uploaded_file = UploadedFile(original_name=file.filename, sha256=hash_value, uploaded_at=datetime.now(UTC))
            session.add(uploaded_file)
            session.flush()
            parse_csv_to_workout(file_path=file_path, uf_id=uploaded_file.id, session=session, user_id=user.id)
            session.commit()
            success_count += 1

        except ParseCsvError:
            session.rollback()
            type_err_count += 1
        except FileValidationError:
            session.rollback()
            type_err_count += 1
        except FileAlreadyExistsError:
            session.rollback()
            dup_count += 1
        except OSError:
            session.rollback()
            type_err_count += 1

        except Exception as e:
            session.rollback()
            type_err_count += 1
            print(f"Неизвестная ошибка при загрузке {file.filename}: {e}")  # Для дебага в консоли
    return RedirectResponse(url=f'/imports?success={success_count}&dup={dup_count}&err={type_err_count}',
                            status_code=303)


@app.get('/profile', response_class=HTMLResponse)
async def show_profile(request: Request, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile)).first()
    if user_profile is None:
        return RedirectResponse(url='/profile/create', status_code=303)
    athlete_profile = session.exec(select(AthleteProfile).where(AthleteProfile.id == user_profile.id)).first()
    return templates.TemplateResponse('profile.html', {'request': request, 'user_profile': user_profile,
                                                       'athlete_profile': athlete_profile})


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
        current_ftp: int = Form(...),
        limitations: str = Form(...),
        weekly_hours: float = Form(...),
        gear: str = Form(...),
        environment_location: str = Form(...),
        birth_date: Optional[date] = Form(None),
        height_cm: Optional[int] = Form(None),
        email_address: str = Form(...),
        session: Session = Depends(get_session)
):
    if session.exec(select(UserProfile)).first() is None:
        user_profile = UserProfile(name=name, birth_date=birth_date, height_cm=height_cm, email_address=email_address)
        session.add(user_profile)
        session.commit()
        athlete_profile = AthleteProfile(id=user_profile.id, weight_kg=weight_kg, current_ftp=current_ftp, gear=gear,
                                         environment_location=environment_location, limitations=limitations,
                                         weekly_hours=weekly_hours)
        session.add(athlete_profile)
        session.commit()

    return RedirectResponse(url='/profile', status_code=303)


@app.get('/profile/edit', response_class=HTMLResponse)
async def check_edited_profile(request: Request, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile)).first()

    if user_profile is not None:
        athlete_profile = session.exec(select(AthleteProfile).where(AthleteProfile.id == user_profile.id)).first()
        return templates.TemplateResponse('profile_edit.html', {'request': request, 'user_profile': user_profile,
                                                                'athlete_profile': athlete_profile})

    return RedirectResponse(url='/profile/create', status_code=303)


@app.post('/profile/edit', response_class=HTMLResponse)
async def edit_profile(
        name: str = Form(...),
        email_address: str = Form(...),
        weight_kg: float = Form(...),
        current_ftp: int = Form(...),
        weekly_hours: float = Form(...),
        gear: str = Form(...),
        environment_location: str = Form(...),
        limitations: str = Form(...),
        birth_date: Optional[date] = Form(None),
        height_cm: Optional[int] = Form(None),
        session: Session = Depends(get_session)
):
    # Получаем данные из базы
    user_profile = session.exec(select(UserProfile)).first()
    athlete_profile = session.exec(select(AthleteProfile).where(AthleteProfile.id == user_profile.id)).first()

    # Обновляем UserProfile
    user_profile.name = name
    user_profile.email_address = email_address
    user_profile.birth_date = birth_date
    user_profile.height_cm = height_cm
    user_profile.updated_at = datetime.now()

    # Обновляем AthleteProfile
    athlete_profile.weight_kg = weight_kg
    athlete_profile.current_ftp = current_ftp
    athlete_profile.weekly_hours = weekly_hours
    athlete_profile.gear = gear
    athlete_profile.environment_location = environment_location
    athlete_profile.limitations = limitations

    # Сохраняем, отправляем в базу
    session.add(user_profile)
    session.add(athlete_profile)
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
    user_profile = session.exec(select(UserProfile)).first()
    if not user_profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    athlete_profile = session.exec(select(AthleteProfile).where(AthleteProfile.id == user_profile.id)).first()

    week_ago = datetime.now() - timedelta(days=7)
    workouts = session.exec(select(Workout).join(UploadedFile).where(UploadedFile.uploaded_at >= week_ago)).all()
    summary = ollama_service.format_workouts(workouts)
    message_history = session.exec(select(ChatMessage).where(ChatMessage.user_id == user_profile.id).where(
        ChatMessage.created_at >= week_ago)).all()
    prompt = await ollama_service.build_chat_messages(user_profile=user_profile, athlete_profile=athlete_profile,
                                                      user_message=user_question, summary=summary,
                                                      message_history=message_history)

    # Сохраняем вопрос пользователя
    user_message = ChatMessage(user_id=user_profile.id, role='user', content=user_question)
    session.add(user_message)
    session.commit()
    # Вызываем ИИ и передаем старую историю + новый вопрос
    answer = await ollama_service.chat(messages=prompt)
    # Сохраняем новый ответ в контекст
    assistant_message = ChatMessage(user_id=user_profile.id, role='assistant', content=answer)
    session.add(assistant_message)
    session.commit()

    return RedirectResponse(url='/coach', status_code=303)


@app.get('/statistics')
async def main_stat(request: Request, session: Session = Depends(get_session), period: int = 7):
    # Делаем запрос к базе данных
    week_ago = datetime.now() - timedelta(days=period)
    workouts_for_range = session.exec(
        select(Workout).join(UploadedFile).where(UploadedFile.uploaded_at >= week_ago)).all()

    # Списки с сырыми данными
    count_workouts = len(workouts_for_range)
    raw_distance = []
    raw_tss = []
    total_moving_time = timedelta(days=0)
    raw_watts = []
    raw_speed = []
    raw_heartrate = []
    raw_cadence = []
    raw_in_factor = []
    raw_norm_power = []
    raw_max_hr = []
    raw_ccall = []
    raw_chart_dates = []

    # Собираем все данные
    for workout in workouts_for_range:
        raw_chart_dates.append(workout.source_file.uploaded_at.strftime('%d.%m'))
        raw_distance.append(workout.distance_km)
        raw_ccall.append(workout.calories_burned)
        raw_tss.append(workout.training_stress_score)
        total_moving_time += workout.duration
        raw_max_hr.append(workout.max_heartrate)
        raw_norm_power.append(workout.normalized_power)
        raw_in_factor.append(workout.intensity_factor)
        raw_cadence.append(workout.avg_cadence)
        raw_watts.append(workout.avg_watts)
        raw_speed.append(workout.avg_speed)
        raw_heartrate.append(workout.avg_heartrate)

    # Очищаем данные от None
    cleaned_in_factor = [el for el in raw_in_factor if el is not None]
    cleaned_np = [el for el in raw_norm_power if el is not None]
    cleaned_tss = [el for el in raw_tss if el is not None]
    cleaned_watts = [el for el in raw_watts if el is not None]
    cleaned_speed = [el for el in raw_speed if el is not None]
    cleaned_heartrate = [el for el in raw_heartrate if el is not None]
    cleaned_cadence = [el for el in raw_cadence if el is not None]
    cleaned_max_hr = [el for el in raw_max_hr if el is not None]
    cleaned_ccall = [el for el in raw_ccall if el is not None]

    # Рассчитываем значения
    max_in_factor = max(cleaned_in_factor) if cleaned_in_factor else 0
    max_distance = max(raw_distance) if raw_distance else 0
    max_np = max(cleaned_np) if cleaned_np else 0
    max_heartrate = max(cleaned_max_hr) if cleaned_max_hr else 0
    max_ccall = max(cleaned_ccall) if cleaned_ccall else 0
    avg_heartrate_num = sum(cleaned_heartrate) / len(cleaned_heartrate) if cleaned_heartrate else 0
    avg_speed_num = sum(cleaned_speed) / len(cleaned_speed) if cleaned_speed else 0
    avg_watts_num = sum(cleaned_watts) / len(cleaned_watts) if cleaned_watts else 0
    avg_cadence_num = sum(cleaned_cadence) / len(cleaned_cadence) if cleaned_cadence else 0
    total_ccall = sum(cleaned_ccall) if cleaned_ccall else 0
    total_tss_num = sum(cleaned_tss) if cleaned_tss else 0
    return templates.TemplateResponse('statistics.html', {'request': request, 'count_workouts': count_workouts,
                                                          'raw_total_distance': raw_distance,
                                                          'total_tss_num': total_tss_num,
                                                          'total_moving_time': total_moving_time,
                                                          'avg_watts_num': avg_watts_num,
                                                          'avg_speed_num': avg_speed_num,
                                                          'avg_heartrate_num': avg_heartrate_num,
                                                          'max_in_factor': max_in_factor, 'max_distance': max_distance,
                                                          'max_np': max_np, 'max_heartrate': max_heartrate,
                                                          'avg_cadence_num': avg_cadence_num, 'period': period,
                                                          'total_ccall': total_ccall, 'max_ccall': max_ccall,
                                                          'raw_distance': raw_distance, 'raw_tss': raw_tss,
                                                          'raw_watts': raw_watts, 'raw_speed': raw_speed,
                                                          'raw_heartrate': raw_heartrate, 'raw_cadence': raw_cadence,
                                                          'raw_in_factor': raw_in_factor,
                                                          'raw_norm_power': raw_norm_power, 'raw_max_hr': raw_max_hr,
                                                          'raw_ccall': raw_ccall, 'raw_chart_dates': raw_chart_dates})
