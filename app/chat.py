
"""Customer-facing AI support chat for Bean & Brew."""

import uuid

import streamlit as st
import logging
from database import (
    create_conversation,
    get_conversation_history,
    get_customer_conversations,
    get_conversation_by_id,
    create_customer_ticket,
    save_message,
)
logger = logging.getLogger(__name__)
from rag.rag_pipeline import RAGPipeline

def is_human_support_request(message: str) -> bool:
    """Check whether the customer explicitly requests human assistance."""

    human_support_phrases = [
        "speak to a human",
        "talk to a human",
        "speak to an agent",
        "talk to an agent",
        "live agent",
        "human support",
        "customer support representative",
        "connect me to support",
        "connect me to an agent",
        "real person",
    ]

    message = message.lower()

    return any(
        phrase in message
        for phrase in human_support_phrases
    )


def show_chat(customer):
    """Display the authenticated customer's AI support chat."""

    customer_id = customer["id"]

    # Initialise a separate chat for each customer.
    if st.session_state.get("chat_customer_id") != customer_id:
        st.session_state.chat_customer_id = customer_id
        st.session_state.chat_session_id = uuid.uuid4().hex
        st.session_state.rag_pipeline = RAGPipeline()

        st.session_state.chat_conversation_id = create_conversation(
            session_id=st.session_state.chat_session_id,
            customer_id=customer_id,
        )

        st.session_state.pending_ticket_issue = None

    session_id = st.session_state.chat_session_id

    st.title("AI Support Assistant")

    st.caption(
        "Ask me about Bean & Brew's products, orders, payments, "
        "shipping, and store policies."
    )

    st.info(
        "I'm Bean & Brew's AI assistant. I can answer questions using "
        "our store information and help you raise a support request."
    )
        # Display the customer's saved AI conversations.
    conversations = get_customer_conversations(customer_id)

    conversation_options = [None] + [
        conversation["id"] for conversation in conversations
    ]

    conversation_lookup = {
        conversation["id"]: conversation
        for conversation in conversations
    }

    active_id = st.session_state.chat_conversation_id

    selected_conversation = st.selectbox(
        "Previous conversations",
        options=conversation_options,
        index=(
            conversation_options.index(active_id)
            if active_id in conversation_options
            else 0
        ),
        format_func=lambda conversation_id: (
            "Select a saved conversation"
            if conversation_id is None
            else (
                f"{conversation_lookup[conversation_id]['created_at']} - "
                f"{(conversation_lookup[conversation_id]['first_message'] or 'Conversation')[:45]}"
            )
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Open conversation",
            use_container_width=True,
            disabled=selected_conversation is None,
        ):
            conversation = get_conversation_by_id(
                selected_conversation,
                customer_id,
            )

            if conversation:
                st.session_state.chat_conversation_id = conversation["id"]
                st.session_state.chat_session_id = conversation["session_id"]
                st.session_state.pending_ticket_issue = None
                st.rerun()

    with col2:
        if st.button(
            "+ New conversation",
            use_container_width=True,
        ):
            new_session_id = uuid.uuid4().hex

            new_conversation_id = create_conversation(
                session_id=new_session_id,
                customer_id=customer_id,
            )

            st.session_state.chat_session_id = new_session_id
            st.session_state.chat_conversation_id = new_conversation_id
            st.session_state.pending_ticket_issue = None
            st.rerun()

    # Load and display conversation history.
    history = get_conversation_history(session_id)

    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept a new customer message.
    question = st.chat_input("How can I help you today?")

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        save_message(
            st.session_state.chat_conversation_id,
            "user",
            question,
        )

        try:
            with st.chat_message("assistant"):
                with st.spinner("Looking into that for you..."):

                    response = st.session_state.rag_pipeline.answer(
                        question=question,
                        history=history,
                    )

                    answer = response["answer"]
                    sources = response["sources"]

                    st.markdown(answer)

                    if sources:
                        with st.expander("Knowledge-base sources"):
                            for source in sources:
                                st.write(f"- {source}")

                    save_message(
                        st.session_state.chat_conversation_id,
                        "assistant",
                        answer,
                    )


                    # Offer ticket creation for unanswered questions or human-support requests.
                    if not sources or is_human_support_request(question):
                        st.session_state.pending_ticket_issue = question

        except Exception as error:
            st.error(
                "I'm sorry, I couldn't process your request "
                "right now. Please try again."
            )
            logger.exception("Failed to process customer chat message")

    # Display ticket confirmation immediately after processing.
    if st.session_state.get("pending_ticket_issue"):

        st.warning(
            "Would you like me to create a support ticket "
            "for this unanswered question?"
        )

        st.write(
            f"**Your question:** "
            f"{st.session_state.pending_ticket_issue}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Create support ticket",
                use_container_width=True,
                key="confirm_create_ticket",
            ):
                try:
                    ticket_id = create_customer_ticket(
                        customer_id=customer_id,
                        issue=st.session_state.pending_ticket_issue,
                    )

                    save_message(
                        st.session_state.chat_conversation_id,
                        "assistant",
                        f"Your support ticket has been created successfully. "
                        f"Your ticket ID is **{ticket_id}**.",
                    )

                    st.session_state.pending_ticket_issue = None

                    st.success(
                        f"Your support ticket has been created! "
                        f"Ticket ID: {ticket_id}"
                    )

                except Exception as error:
                    st.error("Unable to create your ticket right now.")
                    logger.exception("Failed to create customer support ticket")

        with col2:
            if st.button(
                "No, thanks",
                use_container_width=True,
                key="cancel_create_ticket",
            ):
                st.session_state.pending_ticket_issue = None

                save_message(
                    st.session_state.chat_conversation_id,
                    "assistant",
                    "No problem! Let me know if you need anything else.",
                )

                st.rerun()
