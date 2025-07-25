import json
import logging
from groq import Groq
import openai
import google.generativeai as genai

logger = logging.getLogger(__name__)


def create_quest_from_setting(setting_text: str, api_key: str, api_provider: str):
    client = None
    model = ""
    if api_provider == "groq":
        client = Groq(api_key=api_key)
        model = "llama3-8b-8192"
    elif api_provider == "openai":
        openai.api_key = api_key
        client = openai.ChatCompletion
        model = "gpt-4"
    elif api_provider == "gemini":
        genai.configure(api_key=api_key)
        client = genai.GenerativeModel('gemini-pro')
        model = "gemini-pro"

    master_prompt = f"""
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

    try:
        if api_provider == "gemini":
            response = client.generate_content(master_prompt)
            response_content = response.text
        else:
            chat_completion = client.create(
                messages=[
                    {
                        "role": "user",
                        "content": master_prompt,
                    }
                ],
                model=model,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_content = chat_completion.choices[0].message.content

        if response_content is None:
            logger.error("LLM returned no content.")
            return {"error": "LLM returned no content."}

        return json.loads(response_content)

    except Exception as e:
        logger.error(f"An error occurred while generating quest: {e}")
        return {"error": str(e)}
