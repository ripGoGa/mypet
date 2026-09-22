class ProfileAlreadyExistsError(Exception):
    """Ошибка в создании пользователя"""
    pass


class UserAlreadyExistError(Exception):
    """Данный пользователь уже существует"""


class UserEmailPasswordError(Exception):
    """Пользователь не найден или не верный пароль"""


class MissingWorkoutError(Exception):
    """Тренировка не найдена"""


class AIProviderNotAvailable(Exception):
    """"Сервис ИИ не доступен"""


class AIProviderTimeOut(Exception):
    """"Превышено время ожидания"""


class AIProvideInternalError(Exception):
    """"Внутренняя ошибка ИИ"""


class DownloadPromptError(Exception):
    """"Произошла ошибка файл промпта не найден"""

class ParseFitError(Exception):
    """Ошибка в парсере FIT-файлов"""

class MultiSessionError(ParseFitError):
    """Файл содержит 2 или более сессии"""

class ZeroSessionError(ParseFitError):
    """Файл не содержит сессии"""