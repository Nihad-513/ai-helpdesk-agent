from dotenv import load_dotenv
from llm import groq_chat

load_dotenv()

response = groq_chat(
    messages=[
        {
            "role": "user",
            "content": "A customer asks how long shipping takes. Reply politely."
        }
    ],
    system="You are a friendly customer support assistant for Bean & Brew."
)

print("\nGroq response:")
print(response)