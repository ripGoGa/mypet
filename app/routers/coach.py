from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_current_user, get_chat_repo
from app.main import templates
from app.models.models import Users
from app.repository.chat_repo import ChatRepository

router = APIRouter()


@router.get('/coach')
def coach(request: Request, user: Users = Depends(get_current_user),
          chat_repo: ChatRepository = Depends(get_chat_repo)):
    if not user.user_profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    message_history = chat_repo.get_all_chat_history(user_id=user.id)
    return templates.TemplateResponse(request, 'coach.html', {'message_history': message_history})
