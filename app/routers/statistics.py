from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.core.dependencies import get_current_user, get_statistics_service
from app.core.templating import templates
from app.models.models import Users
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get('/statistics')
def main_stat(request: Request, user: Users = Depends(get_current_user), period: int = 0,
              service: StatisticsService = Depends(get_statistics_service)):
    work_dto = service.get_user_stats(user_id=user.id, period=period).model_dump()
    work_dto['period'] = period

    return templates.TemplateResponse(request, 'statistics.html', work_dto)

