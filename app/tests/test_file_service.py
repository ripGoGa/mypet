from app.services.file_service import delete_file


def test_delete_file(tmp_path) -> None:
    empty_file_path = tmp_path / 'empty.csv'
    empty_file_path.write_text('')
    assert empty_file_path.exists()
    delete_file(str(empty_file_path))
    assert not empty_file_path.exists()

def test_delete_missing_file(tmp_path) -> None:
    empty_file_path = tmp_path / 'empty.csv'
    assert not empty_file_path.exists()
    delete_file(str(empty_file_path))