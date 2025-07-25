from unittest.mock import MagicMock, patch

from services.quest_generator import create_quest_from_setting, validate_api_key 


@patch("services.quest_generator.Groq") 
def test_create_quest_groq_success(mock_groq):
    """Тестирует успешный путь с провайдером Groq."""
    mock_response_content = '{"questTitle": "Успешный тест Groq"}'
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = mock_response_content
    mock_groq.return_value.chat.completions.create.return_value = mock_completion
    result = create_quest_from_setting("любой сеттинг", "fake_key", "groq")
    assert result == {"questTitle": "Успешный тест Groq"}
    mock_groq.return_value.chat.completions.create.assert_called_once()


@patch("services.quest_generator.openai.OpenAI") 
def test_create_quest_openai_success(mock_openai):
    """Тестирует успешный путь с провайдером OpenAI."""
    mock_response_content = '{"questTitle": "Успешный тест OpenAI"}'
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = mock_response_content
    mock_openai.return_value.chat.completions.create.return_value = mock_completion
    result = create_quest_from_setting("любой сеттинг", "fake_key", "openai")
    assert result == {"questTitle": "Успешный тест OpenAI"}
    mock_openai.return_value.chat.completions.create.assert_called_once()


@patch("services.quest_generator.genai") 
def test_create_quest_gemini_success(mock_genai):
    """Тестирует успешный путь с провайдером Gemini."""
    mock_response = MagicMock()
    mock_response.text = '{"questTitle": "Успешный тест Gemini"}'
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    result = create_quest_from_setting("любой сеттинг", "fake_key", "gemini")
    assert result == {"questTitle": "Успешный тест Gemini"}
    mock_genai.configure.assert_called_once_with(api_key="fake_key")


@patch("services.quest_generator.Groq") 
def test_create_quest_api_error(mock_groq):
    """Тестирует случай, когда API (на примере Groq) возвращает ошибку."""
    mock_groq.return_value.chat.completions.create.side_effect = Exception("API Error")
    result = create_quest_from_setting("любой сеттинг", "fake_key", "groq")
    assert "error" in result
    assert result["error"] == "API Error"


@patch("services.quest_generator.Groq") 
def test_create_quest_no_content(mock_groq):
    """Тестирует случай, когда API (на примере Groq) не вернуло контент."""
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = None
    mock_groq.return_value.chat.completions.create.return_value = mock_completion
    result = create_quest_from_setting("любой сеттинг", "fake_key", "groq")
    assert "error" in result
    assert result["error"] == "LLM returned no content."


@patch("services.quest_generator.Groq") # ИСПРАВЛЕНО
def test_validate_key_groq_success(mock_groq):
    """Тестирует успешную валидацию ключа Groq."""
    mock_groq.return_value.models.list.return_value = MagicMock()
    assert validate_api_key("groq", "valid") == {"status": "ok"}


@patch("services.quest_generator.openai.OpenAI") # ИСПРАВЛЕНО
def test_validate_key_openai_success(mock_openai):
    """Тестирует успешную валидацию ключа OpenAI."""
    mock_openai.return_value.models.list.return_value = MagicMock()
    assert validate_api_key("openai", "valid") == {"status": "ok"}


@patch("services.quest_generator.genai") # ИСПРАВЛЕНО
def test_validate_key_gemini_success(mock_genai):
    """Тестирует успешную валидацию ключа Gemini."""
    mock_model = MagicMock()
    mock_model.supported_generation_methods = ["generateContent"]
    mock_genai.list_models.return_value = [mock_model]
    assert validate_api_key("gemini", "valid") == {"status": "ok"}
    mock_genai.configure.assert_called_once_with(api_key="valid")


@patch("services.quest_generator.genai") # ИСПРАВЛЕНО
def test_validate_key_gemini_no_models(mock_genai):
    """Тестирует валидацию Gemini, когда не найдено подходящих моделей."""
    mock_genai.list_models.return_value = []
    result = validate_api_key("gemini", "no-models-key")
    assert result["status"] == "error"
    assert "Ошибка проверки ключа" in result["message"]


@patch("services.quest_generator.Groq") # ИСПРАВЛЕНО
def test_validate_key_api_error_401(mock_groq):
    """Тестирует обработку ошибки 401 (неверный ключ)."""
    mock_groq.return_value.models.list.side_effect = Exception("401 Invalid Key")
    result = validate_api_key("groq", "invalid")
    assert result == {"status": "error", "message": "Неверный API ключ."}


@patch("services.quest_generator.Groq") # ИСПРАВЛЕНО
def test_validate_key_generic_api_error(mock_groq):
    """Тестирует обработку общей ошибки API."""
    mock_groq.return_value.models.list.side_effect = Exception("Connection Timeout")
    result = validate_api_key("groq", "bad-connection")
    assert result == {
        "status": "error",
        "message": "Ошибка проверки ключа. См. логи сервера.",
    }


def test_validate_key_unknown_provider():
    """Тестирует валидацию с неизвестным провайдером."""
    result = validate_api_key("foobar", "any_key")
    assert result == {"status": "error", "message": "Unknown API provider: foobar"}