# from llama_cpp import Llama
# #from config import LLM_MODEL_PATH

# LLM_MODEL_PATH="/app/model/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
# llm = Llama(model_path=LLM_MODEL_PATH, n_ctx=2048)

# def generate_answer(context: str, question: str) -> str:
#     prompt = f"""
# Context:
# {context}

# Question: {question}
# Answer:
# """
#     output = llm(prompt, stop=["\n"], max_tokens=256)
#     return output['choices'][0]['text'].strip()