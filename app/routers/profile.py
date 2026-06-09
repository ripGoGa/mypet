from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.dependencies import get_current_user
from app.core.exceptions import ProfileAlreadyExistsError
from app.core.templating import templates
from app.models.models import Users
from app.schemas.profile import ProfileCreateDTO
from app.services.profile_service import ProfileService, get_profile_service

router = APIRouter()


@router.post('/profile/edit')
async def edit_profile(
        name: str = Form(...),
        weight_kg: float = Form(...),
        current_ftp: int = Form(...),
        limitations: str = Form(...),
        weekly_hours: float = Form(...),
        gear: str = Form(...),
        environment_location: str = Form(...),
        birth_date: Optional[date] = Form(None),
        height_cm: Optional[int] = Form(None),
        service: ProfileService = Depends(get_profile_service),
        user: Users = Depends(get_current_user)
):
    profile = ProfileCreateDTO(name=name, weight_kg=weight_kg, current_ftp=current_ftp, limitations=limitations,
                               weekly_hours=weekly_hours, gear=gear, environment_location=environment_location,
                               birth_date=birth_date, height_cm=height_cm)
    service.edit_profile(user_data=profile, user_id=user.id)
    return RedirectResponse(url='/profile', status_code=303)


@router.post("/profile/create")
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
        service: ProfileService = Depends(get_profile_service),
        user: Users = Depends(get_current_user)):
    try:
        profile = ProfileCreateDTO(name=name, weight_kg=weight_kg, current_ftp=current_ftp, limitations=limitations,
                                   weekly_hours=weekly_hours, gear=gear, environment_location=environment_location,
                                   birth_date=birth_date, height_cm=height_cm)
        service.create_new_profile(user_data=profile, user_id=user.id)
    except ProfileAlreadyExistsError:
        raise HTTPException(status_code=400, detail='Профиль уже существует')
    return RedirectResponse(url='/profile', status_code=303)


@router.get('/profile')
def show_profile(request: Request, user: Users = Depends(get_current_user)):
    if user.user_profile is None:
        return RedirectResponse(url='/profile/create', status_code=303)
    return templates.TemplateResponse(request, 'profile.html', {'user_profile': user.user_profile,
                                                                'athlete_profile': user.athlete_profile})


@router.get('/profile/create')
async def check_created_profile(request: Request, user: Users = Depends(get_current_user)):
    if user.user_profile is None:
        return templates.TemplateResponse(request, 'profile_create.html')
    return RedirectResponse(url='/profile', status_code=303)


@router.get('/profile/edit')
async def check_edited_profile(request: Request,
                               user: Users = Depends(get_current_user)):
    user_profile = user.user_profile

    if user_profile is not None:
        athlete_profile = user.athlete_profile
        return templates.TemplateResponse(request, 'profile_edit.html', {'user_profile': user_profile,
                                                                         'athlete_profile': athlete_profile})

    return RedirectResponse(url='/profile/create', status_code=303)
