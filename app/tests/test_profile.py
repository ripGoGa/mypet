def test_create_profile_success(authorized_client):
    profile_data = {'name': 'Igor', 'weight_kg': 70.5, 'current_ftp': 270,
                    'limitations': 'правая нога значительно сильнее левой', 'weekly_hours': 7.5, 'gear': 'велосипед',
                    'environment_location': 'Куала Лумпур', 'birth_date': '1991-10-15', 'height_cm': 181}
    response = authorized_client.post('/profile/create', data=profile_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Igor' in response.text
    assert '70.5' in response.text


def test_create_profile_double_error(authorized_client):
    profile_data = {'name': 'Igor', 'weight_kg': 70.5, 'current_ftp': 270,
                    'limitations': 'правая нога значительно сильнее левой', 'weekly_hours': 7.5, 'gear': 'велосипед',
                    'environment_location': 'Куала Лумпур', 'birth_date': '1991-10-15', 'height_cm': 181}
    response_1 = authorized_client.post('/profile/create', data=profile_data, follow_redirects=False)
    response_2 = authorized_client.post('/profile/create', data=profile_data, follow_redirects=False)
    print(response_2.text)
    assert response_2.status_code == 400
    assert 'Профиль уже существует' in response_2.text


def test_non_auth_user_error(client):
    response1 = client.post('/profile/create')
    response2 = client.get('/profile/create')
    assert response1.status_code == 401
    assert response2.status_code == 401


def test_edit_profile_success(authorized_client):
    profile_data = {'name': 'Igor', 'weight_kg': 70.5, 'current_ftp': 270,
                    'limitations': 'правая нога значительно сильнее левой', 'weekly_hours': 7.5, 'gear': 'велосипед',
                    'environment_location': 'Куала Лумпур', 'birth_date': '1991-10-15', 'height_cm': 181}
    authorized_client.post('/profile/create', data=profile_data, follow_redirects=True)
    edit_profile = {'name': 'Mike', 'weight_kg': 70.5, 'current_ftp': 270,
                    'limitations': 'правая нога значительно сильнее левой', 'weekly_hours': 7.5, 'gear': 'велосипед',
                    'environment_location': 'Куала Лумпур', 'birth_date': '1991-10-15', 'height_cm': 181}
    response = authorized_client.post('/profile/edit', data=edit_profile)
    assert response.status_code == 200
    assert 'Mike' in response.text
