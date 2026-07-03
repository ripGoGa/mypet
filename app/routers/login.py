from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_user_service
from app.core.exceptions import UserEmailPasswordError
from app.core.templating import templates
from app.services.security import create_access_token
from app.services.user_service import UserService

router = APIRouter()


@router.post('/login')
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
          service: UserService = Depends(get_user_service)):
    try:
        # Looking and verifying a user
        user = service.authenticate_user(email=form_data.username, password=form_data.password)
        # Create the jwt_token
        jwt_token = create_access_token(data={'sub': form_data.username})
        if user.user_profile is None:
            redirect_url = '/profile/create'
        else:
            redirect_url = '/'
        response = RedirectResponse(url=redirect_url, status_code=303)
        response.set_cookie(key='access_token', value=jwt_token, httponly=True)
    except UserEmailPasswordError:
        raise HTTPException(status_code=400, detail='Неверный логин или пароль')
    return response


@router.get('/login')
def get_login_page(request: Request):
    # Показываем страницу в браузере
    return templates.TemplateResponse(request, 'login.html')


@router.get('/logout')
def get_logout(request: Request):
    response = RedirectResponse(url='/?logged_out=true', status_code=303)
    response.delete_cookie(key='access_token')
    return response
