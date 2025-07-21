import json
import pytest
from unittest.mock import patch
from backend.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("backend.app.create_quest")
def test_generate_endpoint_with_mock(mock_create_quest, client):
    mock_response = {"questTitle": "Тестовый квест", "startNodeId": "start"}
    mock_create_quest.return_value = mock_response

    # Выносим данные запроса в отдельную переменную для читаемости
    request_payload = {
        "setting": "любой сеттинг",
        "model": "groq",
        "api_key": "любой_ключ",
    }

    # Теперь вызов функции стал короче и чище
    response = client.post(
        "/generate",
        data=json.dumps(request_payload),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json == mock_response
    # Проверяем вызов с теми же параметрами
    mock_create_quest.assert_called_once_with("любой сеттинг", "groq", "любой_ключ")
