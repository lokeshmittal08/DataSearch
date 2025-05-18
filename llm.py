from llama_cpp import Llama
#from config import LLM_MODEL_PATH
import os

LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH")

llm = Llama(model_path=LLM_MODEL_PATH, n_ctx=2048)

def generate_answer(context: str, question: str) -> str:
    prompt = f"""
Context:
{context}

Question: {question}
Answer:
"""
    output = llm(prompt, stop=["\n"], max_tokens=256)
    return output['choices'][0]['text'].strip()