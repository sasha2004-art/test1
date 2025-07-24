import pytest
from unittest.mock import MagicMock, patch
from services.quest_generator import create_quest_from_setting


@patch("services.quest_generator.Groq")
def test_create_quest_success(mock_groq):
    """Тестирует успешный путь: API вернуло валидный JSON."""
    mock_response_content = '{"questTitle": "Успешный тест"}'
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = mock_response_content
    mock_groq.return_value.chat.completions.create.return_value = mock_completion

    result = create_quest_from_setting("любой сеттинг", "fake_key")

    assert result == {"questTitle": "Успешный тест"}
    mock_groq.return_value.chat.completions.create.assert_called_once()

@patch("services.quest_generator.Groq")
def test_create_quest_api_error(mock_groq):
    """Тестирует случай, когда API возвращает ошибку."""
    mock_groq.return_value.chat.completions.create.side_effect = Exception("API Error")

    result = create_quest_from_setting("любой сеттинг", "fake_key")

    assert "error" in result
    assert result["error"] == "API Error"

@patch("services.quest_generator.Groq")
def test_create_quest_no_content(mock_groq):
    """Тестирует случай, когда API не вернуло контент (вернуло None)."""
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = None
    mock_groq.return_value.chat.completions.create.return_value = mock_completion

    result = create_quest_from_setting("любой сеттинг", "fake_key")

    assert "error" in result
    assert result["error"] == "LLM returned no content."
