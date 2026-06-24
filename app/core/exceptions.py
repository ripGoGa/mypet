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
