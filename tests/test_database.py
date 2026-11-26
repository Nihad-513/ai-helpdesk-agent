import uuid


import uuid

from database import (
    init_db,
    create_conversation,
    save_message,
    get_conversation_history,
)


def test_conversation_messages_are_saved_and_retrieved():
    init_db()

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

    history = get_conversation_history(session_id)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "How long does shipping take?"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == (
        "Standard shipping takes 3-5 business days."
    )
