
import uuid
from database import (
    init_db,
    register_customer,
    get_customer_by_email,
    create_customer_ticket,
    get_customer_tickets,
    create_conversation,
    get_customer_ticket_replies,
    add_ticket_reply,
)

init_db()

# Create or retrieve two test customers
customers = [
    ("Customer One", "customer1@beanbrew.com"),
    ("Customer Two", "customer2@beanbrew.com"),
]

customer_ids = []

for name, email in customers:
    customer = get_customer_by_email(email)

    if not customer:
        register_customer(name, email, "TestPassword123")
        customer = get_customer_by_email(email)

    customer_ids.append(customer["id"])

customer1_id, customer2_id = customer_ids

# Create separate tickets
ticket1 = create_customer_ticket(
    customer1_id,
    "Payment failed"
)

ticket2 = create_customer_ticket(
    customer2_id,
    "Order delivery delay"
)

print("\nCreated tickets:")
print("Customer 1:", ticket1)
print("Customer 2:", ticket2)

# Test customer ticket retrieval
tickets1 = get_customer_tickets(customer1_id)
tickets2 = get_customer_tickets(customer2_id)

print("\nCustomer 1 tickets:")
for ticket in tickets1:
    print(ticket)

print("\nCustomer 2 tickets:")
for ticket in tickets2:
    print(ticket)

# Verify ticket isolation
customer1_ticket_ids = {
    ticket["ticket_id"] for ticket in tickets1
}

customer2_ticket_ids = {
    ticket["ticket_id"] for ticket in tickets2
}

print("\nTesting customer data isolation:")

print(
    "Customer 1 cannot see Customer 2's ticket:",
    ticket2 not in customer1_ticket_ids
)

print(
    "Customer 2 cannot see Customer 1's ticket:",
    ticket1 not in customer2_ticket_ids
)

# Test customer-linked conversation
#session_id = "test-customer-session-001"
session_id = f"test-session-{uuid.uuid4().hex}"

conversation_id = create_conversation(
    session_id,
    customer1_id
)

print("\nCustomer-linked conversation created!")
print("Conversation ID:", conversation_id)

# Test ticket reply ownership and access control

print("\nTesting ticket reply ownership:")

# Customer 1 must not be able to read Customer 2's ticket replies
customer1_read_customer2_ticket = get_customer_ticket_replies(
    ticket2,
    customer1_id
)

print(
    "Customer 1 cannot read Customer 2's ticket replies:",
    customer1_read_customer2_ticket == []
)

# Customer 1 must not be able to reply to Customer 2's ticket
try:
    add_ticket_reply(
        ticket2,
        "customer",
        customer1_id,
        "Unauthorized reply test"
    )
    print("Customer 1 cannot reply to Customer 2's ticket:", False)

except PermissionError:
    print("Customer 1 cannot reply to Customer 2's ticket:", True)