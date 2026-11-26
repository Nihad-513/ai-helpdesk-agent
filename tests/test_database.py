import uuid


from database import create_conversation, save_message

session_id = f"test-session-{uuid.uuid4().hex}"
conversation_id = create_conversation(session_id)

save_message(
    conversation_id,
    "user",
    "How long does shipping take?",
)

save_message(
    conversation_id,
    "assistant",
    "Standard shipping takes 3-5 business days.",
)

print("Conversation created:", conversation_id)
print("Messages saved successfully!")
