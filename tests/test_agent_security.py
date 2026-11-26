
import pytest

from database import (
    create_staff_account,
    create_support_ticket,
    assign_ticket_to_agent,
    get_agent_tickets,
    update_agent_ticket_status,
    add_ticket_reply,
)


def create_test_agent(name, email):
    return create_staff_account(
        name=name,
        email=email,
        password="TestPassword123",
        role="agent",
    )


def test_agents_can_only_see_their_assigned_tickets():
    agent_a = create_test_agent("Agent A", "agent_a@test.com")
    agent_b = create_test_agent("Agent B", "agent_b@test.com")

    ticket_a = create_support_ticket("Issue for Agent A")
    ticket_b = create_support_ticket("Issue for Agent B")

    assign_ticket_to_agent(ticket_a, agent_a)
    assign_ticket_to_agent(ticket_b, agent_b)

    agent_a_tickets = get_agent_tickets(agent_a)
    agent_b_tickets = get_agent_tickets(agent_b)

    agent_a_ticket_ids = {
        ticket["ticket_id"] for ticket in agent_a_tickets
    }
    agent_b_ticket_ids = {
        ticket["ticket_id"] for ticket in agent_b_tickets
    }

    assert ticket_a in agent_a_ticket_ids
    assert ticket_b not in agent_a_ticket_ids

    assert ticket_b in agent_b_ticket_ids
    assert ticket_a not in agent_b_ticket_ids


def test_agent_cannot_update_another_agents_ticket():
    agent_a = create_test_agent("Agent A", "update_a@test.com")
    agent_b = create_test_agent("Agent B", "update_b@test.com")

    ticket_id = create_support_ticket("Private ticket")
    assign_ticket_to_agent(ticket_id, agent_b)

    with pytest.raises(PermissionError):
        update_agent_ticket_status(
            ticket_id,
            agent_a,
            "Resolved",
        )


def test_agent_cannot_reply_to_another_agents_ticket():
    agent_a = create_test_agent("Agent A", "reply_a@test.com")
    agent_b = create_test_agent("Agent B", "reply_b@test.com")

    ticket_id = create_support_ticket("Private ticket")
    assign_ticket_to_agent(ticket_id, agent_b)

    with pytest.raises(PermissionError):
        add_ticket_reply(
            ticket_id,
            "agent",
            agent_a,
            "Unauthorized reply",
        )
