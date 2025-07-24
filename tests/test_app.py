import json
import pytest
from main import app


@pytest.fixture
def client():
    """Создает тестовый клиент Flask для каждого теста."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_generate_quest_endpoint_success(client, monkeypatch):
    """
    Тестирует успешный ответ от эндпоинта /generate,
    используя monkeypatch для мока функции.
    """
    mock_quest = {
        "questTitle": "Test Quest",
        "startNodeId": "1",
        "nodes": [],
    }

    monkeypatch.setattr(
        "main.create_quest_from_setting",
        lambda setting, api_key: mock_quest,
    )

    request_payload = {
        "setting": "A dark and stormy night",
        "api_key": "test_key",
    }

    response = client.post(
        "/generate",
        data=json.dumps(request_payload),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.get_json() == mock_quest


def test_generate_quest_endpoint_missing_data(client):
    """Тестирует ответ 400 при отсутствии данных в запросе."""
    response = client.post(
        "/generate",
        data=json.dumps({"setting": "A dark and stormy night"}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Missing 'setting' or 'api_key' in request body"
    }


def test_generate_quest_endpoint_generator_error(client, monkeypatch):
    """Тестирует ответ 500, когда генератор квестов возвращает ошибку."""
    error_response = {"error": "Произошла ошибка генерации"}
    monkeypatch.setattr(
        "main.create_quest_from_setting",
        lambda setting, api_key: error_response
    )

    request_payload = {"setting": "любой", "api_key": "любой"}

    response = client.post(
        "/generate",
        data=json.dumps(request_payload),
        content_type="application/json",
    )

    assert response.status_code == 500
    assert response.get_json() == error_response