from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_coach_service, get_current_user
from app.core.templating import templates
from app.models.models import Users
from app.services.coach_service import CoachService

router = APIRouter()


@router.get('/coach')
def coach(request: Request, user: Users = Depends(get_current_user),
          coach_service: CoachService = Depends(get_coach_service)):
    if not user.user_profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    message_history = coach_service.get_chat_history(user_id=user.id)
    return templates.TemplateResponse(request, 'coach.html', {'message_history': message_history})
