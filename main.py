from rag_engine import ask_question

if __name__ == "__main__":
    print("Inside main")
    while True:
        question = input("Ask a question (or 'exit'): ")
        if question.lower() == "exit":
            break
        answer = ask_question(question)
        print(f"\nAnswer: {answer}\n")