from pathlib import Path
from sqlmodel import Session, select
import pandas as pd
from datetime import timedelta

from app.models.models import UserProfile, Workout


class ParseCsvError(Exception):
    """Ошибка в парсере"""
    pass


def parse_csv_to_workout(file_path: Path, uf_id: int, session: Session) -> None:
    df = pd.read_csv(file_path)

    # Маска движения
    if 'moving' in df.columns:
        moving_mask = df['moving'] == True
    else:
        moving_mask = df['velocity_smooth'] > 1

    # Базовые показатели
    p_30 = df.loc[moving_mask, 'watts'].rolling(30).mean()
    ftp = session.exec(select(UserProfile.ftp).where((UserProfile.id == 1))).one()
    duration = timedelta(seconds=df['time'].max())
    moving_time = timedelta(seconds=int(moving_mask.sum()))
    distance_km = round(df['distance'].max() / 1000, 2)
    avg_cadence = int(df.loc[df['cadence'] > 0, 'cadence'].mean())
    avg_heartrate = int(df['heartrate'].mean())
    max_heartrate = int(df['heartrate'].max())
    avg_speed = round(df['velocity_smooth'].mean() * 3.6, 1)
    avg_speed_without_stop = round(df.loc[df['velocity_smooth'] > 2, 'velocity_smooth'].mean() * 3.6, 1)

    # Метрики
    avg_watts = int(df.loc[moving_mask, 'watts'].mean())
    normalized_power = round(((p_30 ** 4).mean()) ** 0.25, 1)
    intensity_factor = round(normalized_power / ftp, 3)
    training_stress_score = round(((moving_mask.sum() * normalized_power * intensity_factor) / (ftp * 3600)) * 100, 1)

    # Калории
    calories_burned = int(avg_watts * (moving_mask.sum() / 3600) * 3.6)

    # Запись в базу данных
    workout = Workout(source_file_id=uf_id, duration=duration, moving_time=moving_time, distance_km=distance_km,
                            avg_watts=avg_watts, normalized_power=normalized_power, intensity_factor=intensity_factor,
                            training_stress_score=training_stress_score, avg_cadence=avg_cadence, avg_speed=avg_speed,
                            avg_speed_without_stop=avg_speed_without_stop, avg_heartrate=avg_heartrate,
                            max_heartrate=max_heartrate, calories_burned=calories_burned)
    session.add(workout)
    session.flush()
