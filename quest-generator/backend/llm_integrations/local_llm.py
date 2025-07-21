import json
from llama_cpp import Llama

MODEL_PATHS = {
    "phi3-mini": "./models/Phi-3-mini-4k-instruct-q4.gguf",
    "tinyllama": "./models/TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf",
}


def generate_quest_with_local_llm(setting_text: str, model_name: str):
    if model_name not in MODEL_PATHS:
        return {"error": f"Model {model_name} not found."}

    llm = Llama(
        model_path=MODEL_PATHS[model_name],
        chat_format="llama-3",
        n_ctx=2048,
        verbose=False,
    )

    # Упрощенный промпт для локальных моделей
    prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Ты — сценарист. Создай JSON для квеста по описанию.
JSON должен быть валидным.
Весь текст внутри JSON должен быть на русском языке.

Описание: "{setting_text}"

JSON квеста:<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
    try:
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"Local LLM Error: {e}")
        return {"error": str(e)}
