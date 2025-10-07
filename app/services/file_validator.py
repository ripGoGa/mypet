class FileValidationError(Exception):
    """Выбрасывается когда тип файла не подходит"""
    pass


def validate_file_type(filename: str, content_type: str) -> None:
    ct = (content_type or '').lower()
    allowed_ct = {'text/csv'}
    if filename.lower().endswith('.csv') and ct in allowed_ct:
        pass
    else:
        raise FileValidationError('Можно загружать только CSV-файлы!')
