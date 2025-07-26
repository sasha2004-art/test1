import json
import logging
import os
import re
from typing import Any, Dict

import google.generativeai as genai
import openai
from groq import Groq
from llama_cpp import Llama

logger = logging.getLogger(__name__)


def _get_master_prompt(setting_text: str) -> str:
    """Генерирует основной промпт для LLM."""
    return f"""
  Ты — профессиональный геймдизайнер и сценарист. Твоя задача — создать структуру нелинейного квеста в формате JSON на основе предоставленного сеттинга.

  КЛЮЧЕВЫЕ ПРАВИЛА:
  1.  ВЕСЬ СГЕНЕРИРОВАННЫЙ ТЕКСТ (в полях questTitle, title, description, text) ДОЛЖЕН БЫТРО СТРОГО НА РУССКОМ ЯЗЫКЕ.
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
    setting_text: str, api_key: str, api_provider: str, model: str
) -> Dict[str, Any]:
    """Генерирует квест, используя указанного API-провайдера."""
    master_prompt = _get_master_prompt(setting_text)
    response_content = None

    try:
        if api_provider == "groq":
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": master_prompt}],
                model=model,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_content = chat_completion.choices[0].message.content

        elif api_provider == "openai":
            client = openai.OpenAI(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": master_prompt}],
                model=model,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_content = chat_completion.choices[0].message.content

        elif api_provider == "gemini":
            genai.configure(api_key=api_key)  # type: ignore[reportPrivateImportUsage]
            gemini_model = genai.GenerativeModel(model)  # type: ignore
            response = gemini_model.generate_content(master_prompt)
            response_content = response.text

        elif api_provider == "local":
            model_dir = os.getenv("LOCAL_MODEL_PATH", "quest-generator/models")
            model_path = os.path.join(model_dir, model)

            if not os.path.exists(model_path):
                error_msg = f"Локальная модель не найдена по пути: {model_path}"
                logger.error(error_msg)
                return {"error": error_msg}

            llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_gpu_layers=-1,
                verbose=False,
                chat_format="llama-2",  # Используем стандартный формат чата
            )
            chat_completion = llm.create_chat_completion(
                messages=[{"role": "user", "content": master_prompt}],
                temperature=0.7,
                response_format={"type": "json_object"},
                stream=False,  # Явно указываем для корректной работы pyright
            )
            response_content = chat_completion["choices"][0]["message"]["content"]

        else:
            logger.error(f"Unknown API provider: {api_provider}")
            return {"error": f"Unknown API provider: {api_provider}"}

        if response_content is None:
            logger.error("LLM returned no content.")
            return {"error": "LLM returned no content."}

        # Clean response content for markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_content)
        if json_match:
            cleaned_content = json_match.group(1)
        else:
            # If no markdown block found, assume the content is raw JSON
            cleaned_content = response_content

        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse JSON from {api_provider} ({model}). "
                f"Raw content (original): '{response_content}'. "
                f"Cleaned content: '{cleaned_content}'. Error: {e}"
            )
            return {
                "error": "Модель не смогла сгенерировать валидный JSON. "
                "Попробуйте изменить сеттинг или выбрать другую модель/провайдера."
                " (Возможно, модель вернула неполный или некорректный JSON)"
            }

    except Exception as e:
        logger.error(
            f"An error occurred while generating quest with {api_provider}: {e}"
        )
        error_message_lower = str(e).lower()
        # Добавлена проверка на ошибку квоты
        if (
            "quota" in error_message_lower
            or "insufficient_quota" in error_message_lower
        ):
            return {
                "error": "Превышен лимит использования API или недостаточно средств. Пожалуйста, проверьте ваш тарифный план или баланс."
            }
        if "rate limit" in error_message_lower:
            return {"error": "Превышен лимит запросов к API. Попробуйте позже."}
        if (
            "authentication" in error_message_lower
            or "invalid api key" in error_message_lower
            or "401" in error_message_lower
        ):
            return {"error": "Неверный API ключ. Пожалуйста, проверьте ваш ключ."}
        if (
            "model not found" in error_message_lower
            or "model_not_found" in error_message_lower
            or "modelnotfounderror" in error_message_lower
            or "deprecated" in error_message_lower
            or ("404" in error_message_lower and "model" in error_message_lower)
        ):
            return {
                "error": f"Выбранная модель '{model}' не найдена, недоступна или устарела у провайдера {api_provider}. Попробуйте другую модель."
            }

        return {
            "error": f"Произошла ошибка при обращении к API {api_provider}: {str(e)}"
        }


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
            genai.configure(api_key=api_key)  # type: ignore[reportPrivateImportUsage]
            # Проверяем, есть ли доступные модели для генерации текста
            models = [
                m
                for m in genai.list_models()  # type: ignore[reportPrivateImportUsage]
                if "generateContent" in m.supported_generation_methods
            ]
            if not models:
                raise ValueError("No generative models found for this API key.")
            return {"status": "ok"}
        elif api_provider == "local":
            # Для локальных моделей ключ не нужен, всегда считаем 'ok'
            return {"status": "ok"}
        else:
            return {"error": f"Unknown API provider: {api_provider}"}

    except Exception as e:
        logger.error(f"API key validation failed for {api_provider}: {e}")
        # Возвращаем более понятное сообщение об ошибке
        if "401" in str(e) or "invalid" in str(e).lower():
            return {"status": "error", "message": "Неверный API ключ."}
        return {
            "status": "error",
            "message": "Ошибка проверки ключа. См. логи сервера.",
        }


def get_available_models(api_provider: str, api_key: str) -> Dict[str, Any]:
    """Получает и фильтрует список доступных моделей."""
    try:
        models_list = []
        if api_provider == "groq":
            client = Groq(api_key=api_key)
            models = client.models.list().data
            models_list = [model.id for model in models]
        elif api_provider == "openai":
            client = openai.OpenAI(api_key=api_key)
            models = client.models.list().data
            # Фильтруем модели, чтобы исключить те, которые не предназначены для генерации текста
            models_list = [
                model.id
                for model in models
                if "gpt" in model.id.lower() or "text" in model.id.lower()
            ]
        elif api_provider == "gemini":
            genai.configure(api_key=api_key)  # type: ignore[reportPrivateImportUsage]
            models = [
                m.name
                for m in genai.list_models()  # type: ignore[reportPrivateImportUsage]
                if "generateContent" in m.supported_generation_methods
            ]
            models_list = models
        elif api_provider == "local":
            model_dir = os.getenv("LOCAL_MODEL_PATH", "quest-generator/models")
            if not os.path.isdir(model_dir):
                logger.error(f"Директория локальных моделей не найдена: {model_dir}")
                return {"models": []}
            models_list = [
                f
                for f in os.listdir(model_dir)
                if os.path.isfile(os.path.join(model_dir, f)) and f.endswith(".gguf")
            ]
        else:
            return {"error": f"Unknown API provider: {api_provider}"}

        # Удаляем дубликаты и старые версии моделей
        unique_models = {}
        for model in sorted(models_list):
            # Используем regex для удаления дат и версий в конце
            base_name = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", model)
            base_name = re.sub(r"-\d{4}$", "", base_name)
            if base_name not in unique_models:
                unique_models[base_name] = model

        return {"models": list(unique_models.values())}

    except Exception as e:
        logger.error(f"Failed to get models for {api_provider}: {e}")
        return {"error": str(e)}
