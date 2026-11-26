from database import get_connection

session_id = "test-session-002"

with get_connection() as connection:
    conversation = connection.execute(
        """
        SELECT * FROM conversations
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()

    if conversation is None:
        print("Conversation not found.")
    else:
        print("Conversation found:")
        print(dict(conversation))

        messages = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation["id"],),
        ).fetchall()

        print("\nSaved messages:")

        for message in messages:
            print(f"{message['role'].upper()}: {message['content']}")
