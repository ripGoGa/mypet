from datetime import timedelta, datetime, UTC

from sqlmodel import select

from app.models.models import Users, Workout, UploadedFile


def test_get_workouts_list_success(authorized_client, db_test_session):
    user = db_test_session.exec(select(Users).where(Users.email == 'test_client@ya.ru')).first()
    uploaded_file = UploadedFile(original_name='test_ride',
                                 sha256='test',
                                 uploaded_at=datetime.now(UTC),
                                 user_id=user.id)
    db_test_session.add(uploaded_file)
    db_test_session.commit()
    db_test_session.refresh(uploaded_file)
    workout = Workout(duration=timedelta(hours=1, minutes=30),
                      moving_time=timedelta(hours=1, minutes=30),
                      distance_km=45,
                      source_file_id=uploaded_file.id,
                      user_id=user.id
                      )
    db_test_session.add(workout)
    db_test_session.commit()
    response = authorized_client.get("/workouts")
    assert response.status_code == 200
    assert '45.0' in response.text
