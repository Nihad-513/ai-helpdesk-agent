
import uuid

from database import (
    create_conversation,
    save_message,
    get_connection,
)


def test_saved_conversation_and_messages_can_be_retrieved():
    session_id = f"test-session-{uuid.uuid4().hex}"

    conversation_id = create_conversation(session_id)

    save_message(
        conversation_id,
        "user",
        "Where is my order?",
    )

    save_message(
        conversation_id,
        "assistant",
        "Please provide your order ID.",
    )

    # Retrieve the conversation using a fresh database connection.
    with get_connection() as connection:
        conversation = connection.execute(
            """
            SELECT * FROM conversations
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

        assert conversation is not None
        assert conversation["id"] == conversation_id

        messages = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        ).fetchall()

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Where is my order?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Please provide your order ID."
