from pathlib import Path
from sqlmodel import Session, select
import pandas as pd
from datetime import timedelta

from app.models.models import UserProfile


def parse_csv_to_workout(file_path: Path) -> str:
    df = pd.read_csv(file_path)
    p_30 = df['watts'].rolling(30).mean()
    ftp = 242
    # ftp = session.exec(select(UserProfile.ftp).where((UserProfile.id == 1))).one()
    duration = timedelta(seconds=df['time'].max())
    distance_km = round(df['distance'].max() / 1000, 2)
    distance_km2 = round(df['distance'].diff().clip(lower=0).fillna(0).sum() / 1000, 2)
    avg_watts = int(df['watts'].mean())
    normalized_power = round(((p_30**4).mean())**0.25, 0)
    intensity_factor = normalized_power / ftp
    training_stress_score = ((df['time'].max() * normalized_power * intensity_factor) / (ftp * 3600)) * 100
    avg_cadence = df.loc[df['cadence'] > 0, 'cadence'].mean()
    avg_heartrate = df['heartrate'].mean()
    avg_speed = df['velocity_smooth'].mean() * 3.6
    avg_speed_without_stop = df.loc[df['velocity_smooth'] > 2, 'velocity_smooth'].mean() * 3.6
    print(f'duration = {duration}, distance_km = {distance_km},  avg_watts = {avg_watts}, normalized_power = {normalized_power}, intensity_factor ={intensity_factor}, training_stress_score = {training_stress_score}, avg_cadence = {avg_cadence},'
          f'avg_heartrate = {avg_heartrate}, avg_speed = {avg_speed}, avg_speed_without_stop = {avg_speed_without_stop}', sep='\n')



fp = Path('/Users/igoroborin/PycharmProjects/mypet/data/csv/16051339958_streams.csv')

parse_csv_to_workout(file_path=fp)


