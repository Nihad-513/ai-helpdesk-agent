
import uuid
import pytest

from database import (
    register_customer,
    create_customer_ticket,
    get_customer_tickets,
    create_conversation,
    get_customer_ticket_replies,
    add_ticket_reply,
)


def create_test_customer(name, email):
    return register_customer(
        name=name,
        email=email,
        password="TestPassword123",
    )


def test_customers_can_only_see_their_own_tickets():
    customer1_id = create_test_customer(
        "Customer One",
        "customer1@beanbrew.com",
    )
    customer2_id = create_test_customer(
        "Customer Two",
        "customer2@beanbrew.com",
    )

    ticket1 = create_customer_ticket(
        customer1_id,
        "Payment failed",
    )
    ticket2 = create_customer_ticket(
        customer2_id,
        "Order delivery delay",
    )

    tickets1 = get_customer_tickets(customer1_id)
    tickets2 = get_customer_tickets(customer2_id)

    customer1_ticket_ids = {
        ticket["ticket_id"] for ticket in tickets1
    }
    customer2_ticket_ids = {
        ticket["ticket_id"] for ticket in tickets2
    }

    assert ticket1 in customer1_ticket_ids
    assert ticket2 not in customer1_ticket_ids

    assert ticket2 in customer2_ticket_ids
    assert ticket1 not in customer2_ticket_ids


def test_customers_cannot_access_another_customers_ticket_replies():
    customer1_id = create_test_customer(
        "Customer One",
        "reply_customer1@beanbrew.com",
    )
    customer2_id = create_test_customer(
        "Customer Two",
        "reply_customer2@beanbrew.com",
    )

    ticket_id = create_customer_ticket(
        customer2_id,
        "Order delivery delay",
    )

    # The ticket owner can reply successfully.
    assert add_ticket_reply(
        ticket_id,
        "customer",
        customer2_id,
        "Please provide an update.",
    )

    # Another customer cannot read the replies.
    unauthorized_replies = get_customer_ticket_replies(
        ticket_id,
        customer1_id,
    )

    assert unauthorized_replies == []

    # Another customer cannot reply to the ticket.
    with pytest.raises(PermissionError):
        add_ticket_reply(
            ticket_id,
            "customer",
            customer1_id,
            "Unauthorized reply",
        )


def test_customer_linked_conversation_can_be_created():
    customer_id = create_test_customer(
        "Conversation Customer",
        "conversation@beanbrew.com",
    )

    session_id = f"test-session-{uuid.uuid4().hex}"

    conversation_id = create_conversation(
        session_id,
        customer_id,
    )

    assert conversation_id is not None
