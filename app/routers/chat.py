from fastapi import APIRouter, Depends, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_current_user, get_coach_service
from app.models.models import Users
from app.services.coach_service import CoachService

router = APIRouter()


@router.post('/coach/chat')
async def chat(request: Request, user_question: str = Form(...), service: CoachService = Depends(get_coach_service),
               user: Users = Depends(get_current_user)):
    if not user.user_profile:
        return RedirectResponse(url="/profile/create", status_code=303)
    await service.generate_coach_response(user_message=user_question, user=user)
    return RedirectResponse(url='/coach', status_code=303)
