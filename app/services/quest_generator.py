# app/services/quest_generator.py

import json
import logging
from typing import Any, Dict

import google.generativeai as genai
import openai
from groq import Groq

logger = logging.getLogger(__name__)


def _get_master_prompt(setting_text: str) -> str:
    """Генерирует основной промпт для LLM."""
    return f"""
  Ты — профессиональный геймдизайнер и сценарист. Твоя задача — создать структуру нелинейного квеста в формате JSON на основе предоставленного сеттинга.

  КЛЮЧЕВЫЕ ПРАВИЛА:
  1.  ВЕСЬ СГЕНЕРИРОВАННЫЙ ТЕКСТ (в полях questTitle, title, description, text) ДОЛЖЕН БЫТЬ СТРОГО НА РУССКОМ ЯЗЫКЕ.
  2.  JSON должен быть валидным и следовать структуре, описанной ниже.
  3.  Квест должен иметь как минимум 3-4 узла (nodes).
  4.  Обязательно должен быть хотя бы один узел с типом "ENDING_SUCCESS" и один с "ENDING_FAILURE".
  5.  'startNodeId' должен указывать на 'id' одного из узлов.

  Вот требуемая структура JSON:
  {{
    "questTitle": "Название квеста",
    "startNodeId": "id_стартового_узла",
    "nodes": [
    {{
      "id": "уникальный_id_узла",
      "title": "Краткое название сцены",
      "type": "STORY | CHOICE | ENDING_SUCCESS | ENDING_FAILURE",
      "description": "Полное описание сцены, ситуации и окружения.",
      "choices": [
      {{
        "text": "Текст выбора для игрока",
        "targetNodeId": "id_узла_к_которому_ведет_выбор"
      }}
      ]
    }}
    ]
  }}

  Сеттинг для генерации:
  ---
  {setting_text}
  ---

  Теперь сгенерируй JSON для этого квеста на русском языке.
  """


def create_quest_from_setting(
    setting_text: str, api_key: str, api_provider: str
) -> Dict[str, Any]:
    """Генерирует квест, используя указанного API-провайдера."""
    master_prompt = _get_master_prompt(setting_text)
    response_content = None

    try:
        if api_provider == "groq":
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": master_prompt}],
                model="llama3-8b-8192",
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_content = chat_completion.choices[0].message.content

        elif api_provider == "openai":
            client = openai.OpenAI(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": master_prompt}],
                model="gpt-4",
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_content = chat_completion.choices[0].message.content

        elif api_provider == "gemini":
            genai.configure(api_key=api_key)  # type: ignore
            model = genai.GenerativeModel("gemini-pro")  # type: ignore
            response = model.generate_content(master_prompt)
            response_content = response.text

        else:
            logger.error(f"Unknown API provider: {api_provider}")
            return {"error": f"Unknown API provider: {api_provider}"}

        if response_content is None:
            logger.error("LLM returned no content.")
            return {"error": "LLM returned no content."}

        return json.loads(response_content)

    except Exception as e:
        logger.error(
            f"An error occurred while generating quest with {api_provider}: {e}"
        )
        return {"error": str(e)}


def validate_api_key(api_provider: str, api_key: str) -> Dict[str, Any]:
    """Проверяет валидность API-ключа, делая легковесный запрос к провайдеру."""
    try:
        if api_provider == "groq":
            client = Groq(api_key=api_key)
            client.models.list()  # Простой запрос для проверки аутентификации
            return {"status": "ok"}
        elif api_provider == "openai":
            client = openai.OpenAI(api_key=api_key)
            client.models.list()
            return {"status": "ok"}
        elif api_provider == "gemini":
            genai.configure(api_key=api_key)  # type: ignore
            # Проверяем, есть ли доступные модели для генерации текста
            models = [
                m
                for m in genai.list_models()  # type: ignore
                if "generateContent" in m.supported_generation_methods
            ]
            if not models:
                raise ValueError("No generative models found for this API key.")
            return {"status": "ok"}
        else:
            return {
                "status": "error",
                "message": f"Unknown API provider: {api_provider}",
            }

    except Exception as e:
        logger.error(f"API key validation failed for {api_provider}: {e}")
        # Возвращаем более понятное сообщение об ошибке
        if "401" in str(e) or "invalid" in str(e).lower():
            return {"status": "error", "message": "Неверный API ключ."}
        return {
            "status": "error",
            "message": "Ошибка проверки ключа. См. логи сервера.",
        }
