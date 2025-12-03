from api_llm.llm_manager import LLMManager

def test_llm_basic_response():
    llm = LLMManager()
    resultado = llm.consultar_llm("Explica qué es Steam en 10 palabras.")
    
    assert isinstance(resultado, str)
    assert len(resultado) > 2
