from starlette.templating import Jinja2Templates

from app.core.formatter import format_pace, format_stats, format_time

templates = Jinja2Templates(directory="app/templates")

# Фильтры для шаблонов: те же функции, что форматируют сводку для AI-тренера.
templates.env.filters["pace"] = format_pace
templates.env.filters["stats"] = format_stats
templates.env.filters["duration"] = format_time
