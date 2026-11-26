
from database import create_support_ticket, get_support_ticket


def test_support_ticket_creation():
    ticket_id = create_support_ticket(
        issue="Customer wants to know whether international shipping is available.",
        customer_name="Test Customer",
        customer_email="test@example.com",
    )

    assert ticket_id.startswith("BB-")
    assert len(ticket_id) == 11


def test_created_ticket_can_be_retrieved():
    ticket_id = create_support_ticket(
        issue="Where is my order?",
        customer_name="Test Customer",
        customer_email="test@example.com",
    )

    ticket = get_support_ticket(ticket_id)

    assert ticket is not None
    assert ticket["ticket_id"] == ticket_id
    assert ticket["customer_name"] == "Test Customer"
    assert ticket["customer_email"] == "test@example.com"
    assert ticket["issue"] == "Where is my order?"
    assert ticket["status"] == "Open"


def test_nonexistent_ticket_returns_none():
    ticket = get_support_ticket("BB-NOTFOUND")

    assert ticket is None
