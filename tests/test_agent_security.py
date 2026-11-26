from database import (
    init_db,
    get_connection,
    create_support_ticket,
    get_active_agents,
    assign_ticket_to_agent,
    get_agent_tickets,
    update_agent_ticket_status,
    add_ticket_reply,
)

init_db()

# Retrieve the two existing agent accounts
agents = get_active_agents()

print("Active agents:")

for agent in agents:
    print(agent)

# Create two test tickets
ticket_a = create_support_ticket(
    issue="Test ticket assigned to Charles",
    customer_name="Security Test Customer A",
    customer_email="security_a@example.com",
)

ticket_b = create_support_ticket(
    issue="Test ticket assigned to David",
    customer_name="Security Test Customer B",
    customer_email="security_b@example.com",
)

# Assign each ticket to a different agent
assign_ticket_to_agent(ticket_a, 3)
assign_ticket_to_agent(ticket_b, 2)

print("\nTest tickets assigned:")
print("Charles:", ticket_a)
print("David:", ticket_b)

# Retrieve tickets assigned to each agent
charles_tickets = get_agent_tickets(3)
david_tickets = get_agent_tickets(2)

charles_ticket_ids = {
    ticket["ticket_id"] for ticket in charles_tickets
}

david_ticket_ids = {
    ticket["ticket_id"] for ticket in david_tickets
}

print("\nTesting agent ticket isolation:")

print(
    "Charles can access his assigned ticket:",
    ticket_a in charles_ticket_ids
)

print(
    "Charles cannot access David's ticket:",
    ticket_b not in charles_ticket_ids
)

print(
    "David can access his assigned ticket:",
    ticket_b in david_ticket_ids
)

print(
    "David cannot access Charles's ticket:",
    ticket_a not in david_ticket_ids
)
# Test unauthorized status updates

print("\nTesting agent status-update authorization:")

try:
    result = update_agent_ticket_status(
        ticket_b,
        3,
        "Resolved"
    )

    print(
        "Charles cannot update David's ticket:",
        result is False
    )

except PermissionError:
    print("Charles cannot update David's ticket: True")

# Test unauthorized agent replies

print("\nTesting agent reply authorization:")

try:
    result = add_ticket_reply(
        ticket_b,
        "agent",
        3,
        "Unauthorized agent reply test"
    )

    print(
        "Charles cannot reply to David's ticket:",
        result is False
    )

except PermissionError:
    print("Charles cannot reply to David's ticket: True")