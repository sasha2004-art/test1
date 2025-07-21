import pytest
from backend.llm_integrations.factory import get_llm_instance
from backend.llm_integrations.groq_llm import GroqLLM

def test_get_groq_llm_instance():
    instance = get_llm_instance(llm_type='groq', api_key='test-key')
    assert isinstance(instance, GroqLLM)

def test_get_llm_raises_error_for_unknown_type():
    with pytest.raises(ValueError, match="Unknown LLM type"):
        get_llm_instance(llm_type='unknown')

def test_get_groq_llm_raises_error_without_key():
    with pytest.raises(ValueError, match="API key is required"):
        get_llm_instance(llm_type='groq')
