from datetime import datetime, UTC, timedelta
from pathlib import Path
import jwt
from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.requests import Request
from app.core.dependencies import get_current_user
from app.db.session import get_session, create_db_and_tables
from app.models.models import UploadedFile, Workout, ChatMessage, Users
from app.routers import login, register, profile, workout, statistics
from app.services.ai_coach import get_ollama_service
from app.services.file_service import (
    validate_file_type,
    save_file_with_hash,
    FileValidationError,
    FileAlreadyExistsError
)
from app.services.parse_cvs import parse_csv_to_workout, ParseCsvError
from app.services.security import SECRET_KEY, ALGORITHM

app = FastAPI(title="Bike Tracker")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(profile.router)
app.include_router(workout.router)
app.include_router(statistics.router)

templates = Jinja2Templates(directory='app/templates')


def on_startup() -> None:
    create_db_and_tables()


on_startup()


def ensure_data_store() -> None:
    Path('data/csv').mkdir(parents=True, exist_ok=True)


@app.get('/', response_class=HTMLResponse)
async def hello_root(request: Request, session=Depends(get_session)):
    # Пытаемся узнать имя пользователя для приветствия
    token = request.cookies.get('access_token')
    user_profile = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user = session.exec(select(Users).where(Users.email == payload['sub'])).first()
            user_profile = user.user_profile
        except jwt.InvalidTokenError:
            pass

    return templates.TemplateResponse(request, 'index.html', {'user_profile': user_profile})


@app.get('/imports', response_class=HTMLResponse)
async def imports(request: Request, user: Users = Depends(get_current_user)):
    success_count = int(request.query_params.get('success')) if request.query_params.get('success') else 0
    dup_count = int(request.query_params.get('dup')) if request.query_params.get('dup') else 0
    err_count = int(request.query_params.get('err')) if request.query_params.get('err') else 0
    message = None
    if 'success' in request.query_params or 'dup' in request.query_params or 'err' in request.query_params:
        message = f'Успешно загружено: {success_count}, Пропущено дубликатов: {dup_count}, Ошибок: {err_count}'
    return templates.TemplateResponse(request, 'imports.html', {'message': message})


@app.post('/imports')
async def import_csv(files: list[UploadFile] = File(...), session: Session = Depends(get_session),
                     user: Users = Depends(get_current_user)):
    user_profile = user.user_profile
    success_count = 0
    dup_count = 0
    type_err_count = 0

    if not user_profile:
        return RedirectResponse(url='/profile/create', status_code=303)
    for file in files:
        try:
            validate_file_type(filename=file.filename, content_type=file.content_type)
            content = await file.read()
            file_path, hash_value = save_file_with_hash(content, session, user.id)
            uploaded_file = UploadedFile(original_name=file.filename, sha256=hash_value, uploaded_at=datetime.now(UTC),
                                         user_id=user.id)
            session.add(uploaded_file)
            session.flush()
            parse_csv_to_workout(file_path=file_path, uf_id=uploaded_file.id, session=session, user_id=user_profile.id)
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


@app.get('/coach', response_class=HTMLResponse)
async def coach_page(request: Request, session: Session = Depends(get_session),
                     user: Users = Depends(get_current_user)):
    if not user.user_profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    message_history = session.exec(select(ChatMessage).where(user.id == ChatMessage.user_id).order_by(
        ChatMessage.created_at)).all()

    return templates.TemplateResponse(request, 'coach.html', {'message_history': message_history})


@app.post('/coach/chat', response_class=HTMLResponse)
async def chat(request: Request, user_question: str = Form(...), session: Session = Depends(get_session),
               ollama_service=Depends(get_ollama_service), user: Users = Depends(get_current_user)):
    # Получаем данные
    if not user.user_profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    week_ago = datetime.now() - timedelta(days=7)
    workouts = session.exec(select(Workout).join(UploadedFile).where(UploadedFile.uploaded_at >= week_ago,
                                                                     UploadedFile.user_id == user.id)).all()
    summary = ollama_service.format_workouts(workouts)
    message_history = session.exec(select(ChatMessage).where(ChatMessage.user_id == user.id).where(
        ChatMessage.created_at >= week_ago)).all()
    prompt = await ollama_service.build_chat_messages(user_profile=user.user_profile,
                                                      athlete_profile=user.athlete_profile,
                                                      user_message=user_question,
                                                      summary=summary,
                                                      message_history=message_history)

    # Сохраняем вопрос пользователя
    user_message = ChatMessage(user_id=user.id, role='user', content=user_question)
    session.add(user_message)
    session.commit()
    # Вызываем ИИ и передаем старую историю + новый вопрос
    answer = await ollama_service.chat(messages=prompt)
    # Сохраняем новый ответ в контекст
    assistant_message = ChatMessage(user_id=user.id, role='assistant', content=answer)
    session.add(assistant_message)
    session.commit()

    return RedirectResponse(url='/coach', status_code=303)


@app.get('/me')
def me(user=Depends(get_current_user)) -> dict:
    return {'id': user.id, 'email': user.email}


@app.exception_handler(HTTPException)
def error(request: Request, exc: HTTPException):
    status_code = exc.status_code
    detail = exc.detail
    return templates.TemplateResponse(request, 'error.html', {'detail': detail, 'status_code': status_code},
                                      status_code=status_code)
