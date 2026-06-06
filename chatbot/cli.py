from chatbot.agent import chat


def main() -> None:
    thread_id = "cli"
    print("LangGraph multi-tool chatbot. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break
        if not user_input:
            continue

        try:
            answer = chat(user_input, thread_id=thread_id)
        except Exception as exc:
            answer = f"Chat failed: {exc}"
        print(f"\nBot: {answer}")


if __name__ == "__main__":
    main()
