

def test_create_profile_success(authorized_client):
    profile_data = {'name': 'Igor', 'weight_kg': 70.5, 'current_ftp': 270,
                    'limitations': 'правая нога значительно сильнее левой', 'weekly_hours': 7.5, 'gear': 'велосипед',
                    'environment_location': 'Куала Лумпур', 'birth_date': '1991-10-15', 'height_cm': 181}
    response = authorized_client.post('/profile/create', data=profile_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Igor' in response.text
    assert '70.5' in response.text
