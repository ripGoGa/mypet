class ProfileAlreadyExistsError(Exception):
    """"Ошибка в создании пользователя"""
    pass


class UserAlreadyExistError(Exception):
    """"Данный пользователь уже существует"""


class UserEmailPasswordError(Exception):
    """"Пользователь не найден или не верный пароль"""
