import json
from llama_cpp import Llama
from .base import BaseLLM

class LocalMixtralLLM(BaseLLM):
    def __init__(self, model_path: str):
        self.llm = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=-1)

    def generate_quest(self, setting_text: str) -> dict:
        master_prompt = f"""
    Ты — профессиональный геймдизайнер и сценарист.
    Твоя задача — создать структуру нелинейного квеста в формате JSON
    на основе предоставленного сеттинга.

    **КЛЮЧЕВОЕ ПРАВИЛО: Весь генерируемый текст (questTitle, title,
    description, text) ДОЛЖЕН БЫТЬ СТРОГО НА РУССКОМ ЯЗЫКЕ.**

    Правила структуры:
    1. JSON должен быть валидным.
    2. Квест должен иметь 4-5 узлов (nodes).
    3. Обязательно должен быть хотя бы один узел с типом "ENDING_SUCCESS"
       и один с "ENDING_FAILURE".
    4. 'startNodeId' должен указывать на 'id' одного из узлов.

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
            response = self.llm.create_chat_completion(
                messages=[{"role": "user", "content": master_prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            response_content = response['choices'][0]['message']['content']
            return json.loads(response_content)
        except Exception as e:
            print(f"Local LLM error: {e}")
            return {"error": str(e)}
