"""Phase 1: command-line customer support chat for a fictional small business.

Run:
    python chat_cli.py
"""

from llm import chat

SYSTEM_PROMPT = """You are the customer support assistant for Bean & Brew, a small online coffee store.

Rules:
- Be friendly, concise and professional.
- Help with orders, shipping, returns, subscriptions and product questions.
- Only state store policies if you are given them. If you do not know, say so
  and offer to create a support ticket instead of guessing.
- Never ask for full card numbers or passwords.
- If the customer is angry, mentions a payment problem, or asks for a human,
  offer to escalate to a human agent.
"""


def main() -> None:
    history: list[dict] = []
    print("Bean & Brew support (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        try:
            answer = chat(history, SYSTEM_PROMPT)
        except Exception as exc:  # network, auth, quota, etc.
            print(f"[error] {exc}")
            history.pop()
            continue

        history.append({"role": "assistant", "content": answer})
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()