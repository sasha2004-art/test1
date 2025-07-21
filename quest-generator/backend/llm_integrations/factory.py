from .base import BaseLLM
from .groq_llm import GroqLLM
from .local_llm import LocalMixtralLLM

def get_llm_instance(llm_type: str, api_key: str = None, model_path: str = None) -> BaseLLM:
    if llm_type == 'groq':
        if not api_key:
            raise ValueError("API key is required for Groq LLM")
        return GroqLLM(api_key=api_key)
    elif llm_type == 'local_mixtral':
        if not model_path:
            raise ValueError("Model path is required for Local Mixtral LLM")
        return LocalMixtralLLM(model_path=model_path)
    else:
        raise ValueError(f"Unknown LLM type: {llm_type}")
