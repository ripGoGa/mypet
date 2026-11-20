class AppError(Exception):
    """База для всех исключений приложения"""


class ProfileAlreadyExistsError(AppError):
    """Ошибка в создании пользователя"""


class UserAlreadyExistsError(AppError):
    """Данный пользователь уже существует"""


class UserEmailPasswordError(AppError):
    """Пользователь не найден или не верный пароль"""


class MissingWorkoutError(AppError):
    """Тренировка не найдена"""


class CorruptedDataError(AppError):
    """Нарушена целостность данных в базе данных"""


class AIProviderNotAvailableError(AppError):
    """Сервис ИИ не доступен"""


class AIProviderTimeOutError(AppError):
    """Превышено время ожидания"""


class AIProviderInternalError(AppError):
    """Внутренняя ошибка ИИ"""


class DownloadPromptError(AppError):
    """Произошла ошибка файл промпта не найден"""


class ParseFitError(AppError):
    """Ошибка в парсере FIT-файлов"""


class MultiSessionError(ParseFitError):
    """Файл содержит 2 или более сессии"""


class ZeroSessionError(ParseFitError):
    """Файл не содержит сессии"""


class NoSportError(ParseFitError):
    """Файл сессии не содержит данных о спорте"""


class UnsupportedSportError(ParseFitError):
    """Не поддерживаемый вид спорта"""
