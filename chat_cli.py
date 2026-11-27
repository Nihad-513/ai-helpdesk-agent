
"""Command-line customer support application for Bean & Brew."""

import uuid

from database import (
    init_db,
    create_conversation,
    save_message,
    get_conversation_history,
    create_support_ticket,
)
from rag.rag_pipeline import RAGPipeline


def main() -> None:
    # Initialize the database.
    init_db()

    # Create a unique conversation session.
    session_id = f"session-{uuid.uuid4().hex}"

    conversation_id = create_conversation(session_id)

    # Initialize the RAG pipeline.
    rag = RAGPipeline()

    pending_ticket_issue = None
    pending_ticket_name = None
    ticket_creation_step = None
    ticket_confirmation_pending = False

    print("\nBean & Brew AI Support")
    print("Your conversation has started.")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"quit", "exit"}:
            print("\nThank you for contacting Bean & Brew!")
            break

        if not user_input:
            continue

        try:
            # Handle ticket lookup.
            if ticket_lookup_pending:

                ticket_id = user_input.strip().upper()
                ticket = get_support_ticket(ticket_id)

                if ticket:
                    answer = (
                        f"Your ticket {ticket_id} has the status: "
                        f"{ticket['status']}.\n"
                        f"Issue: {ticket['issue']}"
                    )
                else:
                    answer = (
                        f"I couldn't find a ticket with ID {ticket_id}. "
                        "Please check the ID and try again."
                    )

                ticket_lookup_pending = False

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue

            # Handle an explicit ticket confirmation.
            # Handle ticket creation workflow.
            # Handle ticket confirmation.
            if ticket_confirmation_pending:

                if user_input.lower() in {"yes", "yeah", "sure", "y"}:

                    ticket_confirmation_pending = False
                    ticket_creation_step = "name"

                    answer = (
                        "I'd be happy to create a support ticket. "
                        "What's your name? Type 'skip' if you prefer not to share."
                    )

                elif user_input.lower() in {"no", "nope", "n"}:

                    ticket_confirmation_pending = False
                    pending_ticket_issue = None

                    answer = "No problem! I won't create a ticket."
                else:

    # Cancel the pending confirmation and process the new message.
                    ticket_confirmation_pending = False
                    pending_ticket_issue = None

                    history = get_conversation_history(session_id)

                    result = rag.answer(user_input, history)
                    answer = result["answer"]

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue
            if ticket_creation_step == "name":

                pending_ticket_name = (
                    None if user_input.lower() == "skip"
                    else user_input
                )

                ticket_creation_step = "email"
                answer = "Please enter your email address, or type 'skip' to continue without it."

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue

            if ticket_creation_step == "email":

                customer_email = (
                    None if user_input.lower() == "skip"
                    else user_input
                )

                ticket_id = create_support_ticket(
                    issue=pending_ticket_issue,
                    customer_name=pending_ticket_name,
                    customer_email=customer_email,
                )

                answer = (
                    f"Your support ticket has been created successfully! "
                    f"Your ticket ID is {ticket_id}."
                )

                pending_ticket_issue = None
                pending_ticket_name = None
                ticket_creation_step = None

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue

            if pending_ticket_issue:

                if user_input.lower() in {"yes", "yeah", "sure", "y"}:

                    ticket_creation_step = "name"
                    answer = "I'd be happy to create a support ticket. What's your name? You can type 'skip' if you prefer not to share."

                elif user_input.lower() in {"no", "nope", "n"}:

                    pending_ticket_issue = None
                    answer = "No problem! Let me know if you need anything else."

                else:

                    answer = "Please reply yes or no so I know whether to create the support ticket."

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue

            # Detect explicit support escalation requests.
            escalation_phrases = (
                "my payment failed",
                "payment problem",
                "payment issue",
                "speak to a human",
                "talk to a human",
                "human agent",
                "contact support",
                "create a ticket",
                "raise a ticket",
            )

            if any(
                phrase in user_input.lower()
                for phrase in escalation_phrases
            ):
                pending_ticket_issue = user_input
                ticket_confirmation_pending = True

                answer = (
                    "I'm sorry you're experiencing this issue. "
                    "Would you like me to create a support ticket?"
                )

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue
            history = get_conversation_history(session_id)
            # Detect requests to check an existing ticket.
            lookup_phrases = (
                "ticket update",
                "ticket status",
                "check my ticket",
                "track my ticket",
                "ticket progress",
            )

            if any(
                phrase in user_input.lower()
                for phrase in lookup_phrases
            ):
                ticket_lookup_pending = True

                answer = "Sure! Please enter your support ticket ID (for example, BB-8A637FB4)."

                save_message(conversation_id, "user", user_input)
                save_message(conversation_id, "assistant", answer)

                print(f"\nAgent: {answer}\n")
                continue

            # Generate an answer using the conversation history.
            result = rag.answer(user_input, history)
            answer = result["answer"]


            # Save both messages after a successful response.
            save_message(
                conversation_id,
                "user",
                user_input,
            )

            save_message(
                conversation_id,
                "assistant",
                answer,
            )

            print(f"\nAgent: {answer}")

            if result["sources"]:
                print(f"Sources: {', '.join(result['sources'])}")

            print()

        except Exception as exc:
            print(f"\n[error] Something went wrong: {exc}\n")


if __name__ == "__main__":
    main()
