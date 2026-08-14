from fastapi import APIRouter, Depends, Form, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_user_service
from app.core.exceptions import UserAlreadyExistError
from app.core.templating import templates
from app.services.user_service import UserService

router = APIRouter()


@router.post('/register')
def register(request: Request, email: str = Form(...), password: str = Form(...),
             service: UserService = Depends(get_user_service)):
    # call the method for register a new user
    try:
        service.register_new_user(email, password)
    except UserAlreadyExistError:
        raise HTTPException(status_code=400, detail='Данный пользователь уже существует')
    return RedirectResponse(url='/login', status_code=303)


@router.get('/register')
async def get_register_page(request: Request):
    # This just sends the HTML file to the browser
    return templates.TemplateResponse(request, 'register.html')
