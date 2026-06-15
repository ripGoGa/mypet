def test_get_workouts_list_success(authorized_client, load_workout):
    response = authorized_client.get("/workouts?limit=1&period=0")
    assert response.status_code == 200
    assert "Страница 1 из 3" in response.text

