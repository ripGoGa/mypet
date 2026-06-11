from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from app.core.dependencies import get_current_user
from app.core.exceptions import MissingWorkoutError
from app.core.templating import templates
from app.models.models import Users
from app.services.workout_service import WorkoutService, get_workout_service

router = APIRouter()


@router.get('/workouts/{workout_id}')
async def workout_detail(request: Request, workout_id: int, user: Users = Depends(get_current_user),
                         service: WorkoutService = Depends(get_workout_service)):
    try:
        workout = service.get_user_workout(workout_id=workout_id, user_id=user.id)
    except MissingWorkoutError:
        raise HTTPException(status_code=404, detail='Тренировка не найдена')
    return templates.TemplateResponse(request, 'workout_detail.html', {'workout': workout})


@router.get('/workouts')
async def list_workouts(request: Request, service: WorkoutService = Depends(get_workout_service),
                        user: Users = Depends(get_current_user), page: int = 1, period: int = 0,
                        limit: int = 10):
    workouts, total_pages = service.get_user_workouts(user_id=user.id, period=period, page=page, limit=limit)

    return templates.TemplateResponse(request, 'workouts.html', {'workouts': workouts,
                                                                 'current_page': page,
                                                                 'total_pages': total_pages, 'period': period,
                                                                 'limit': limit})
