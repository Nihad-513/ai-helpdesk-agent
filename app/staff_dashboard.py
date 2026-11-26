
"""Bean & Brew staff dashboard."""

import streamlit as st

from database import (
    get_all_tickets,
    get_active_agents,
    assign_ticket_to_agent,
    update_ticket_priority,
    update_ticket_status,
    update_ticket_escalation,
    update_ticket_resolution_notes,
    get_agent_tickets,
    get_ticket_replies,
    add_ticket_reply,
    update_agent_ticket_status,
)
def show_admin_dashboard(staff):
    """Display the administrator ticket overview."""

    tickets = get_all_tickets()
    agents = get_active_agents()
    st.title("Administrator Dashboard")
    st.caption("Monitor and manage customer support requests.")

    # Ticket statistics
    total = len(tickets)
    open_count = sum(t["status"] == "Open" for t in tickets)
    progress_count = sum(t["status"] == "In Progress" for t in tickets)
    resolved_count = sum(t["status"] == "Resolved" for t in tickets)
    escalated_count = sum(bool(t["is_escalated"]) for t in tickets)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Tickets", total)
    col2.metric("Open", open_count)
    col3.metric("In Progress", progress_count)
    col4.metric("Resolved", resolved_count)
    col5.metric("Escalated", escalated_count)

    st.divider()

    # Filters
    st.subheader("Customer Support Tickets")

    filter1, filter2 = st.columns(2)

    with filter1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Open", "In Progress", "Resolved"],
        )

    with filter2:
        priority_filter = st.selectbox(
            "Filter by priority",
            ["All", "Normal", "High", "Urgent"],
        )

    filtered_tickets = tickets

    if status_filter != "All":
        filtered_tickets = [
            t for t in filtered_tickets
            if t["status"] == status_filter
        ]

    if priority_filter != "All":
        filtered_tickets = [
            t for t in filtered_tickets
            if t["priority"] == priority_filter
        ]

    st.caption(f"Showing {len(filtered_tickets)} tickets")

    # Ticket cards
    if not filtered_tickets:
        st.info("No tickets match the selected filters.")

    for ticket in filtered_tickets:
        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {ticket['ticket_id']}")
                st.write(ticket["issue"])

                st.caption(
                    f"Customer: {ticket['customer_name'] or 'Unknown'}"
                )
                st.caption(
                    f"Email: {ticket['customer_email'] or 'Not available'}"
                )
                st.caption(
                    f"Created: {ticket['created_at']}"
                )

                agent = ticket["assigned_agent_name"] or "Unassigned"
                st.caption(f"Assigned agent: {agent}")

            with col2:
                st.write(f"**Status:** {ticket['status']}")
                st.write(f"**Priority:** {ticket['priority']}")

                if ticket["is_escalated"]:
                    st.error("Escalated")

            if ticket["resolution_notes"]:
                st.caption(
                    f"Resolution notes: {ticket['resolution_notes']}"
                )

            st.divider()
            st.markdown("**Ticket Assignment**")

            if agents:
                agent_options = {
                    agent["id"]: agent["name"]
                    for agent in agents
                }

                current_agent = ticket["assigned_agent_id"]

                if current_agent not in agent_options:
                    current_agent = agents[0]["id"]

                selected_agent = st.selectbox(
                    "Assign to support agent",
                    options=list(agent_options.keys()),
                    format_func=lambda agent_id: agent_options[agent_id],
                    index=list(agent_options.keys()).index(current_agent),
                    key=f"agent_select_{ticket['ticket_id']}",
                )

                if st.button(
                    "Assign Ticket",
                    key=f"assign_{ticket['ticket_id']}",
                ):
                    try:
                        success = assign_ticket_to_agent(
                            ticket["ticket_id"],
                            selected_agent,
                        )

                        if success:
                            st.success("Ticket assigned successfully.")
                            st.rerun()
                        else:
                            st.error("Ticket not found.")

                    except ValueError as error:
                        st.error(str(error))

            else:
                st.warning("No active support agents available.")


            st.divider()
            st.markdown("**Manage Ticket**")

            priority_options = ["Normal", "High", "Urgent"]
            status_options = ["Open", "In Progress", "Resolved"]

            current_priority = ticket["priority"]
            current_status = ticket["status"]

            col_priority, col_status = st.columns(2)

            with col_priority:
                new_priority = st.selectbox(
                    "Priority",
                    priority_options,
                    index=priority_options.index(current_priority),
                    key=f"priority_{ticket['ticket_id']}",
                )

                if st.button(
                    "Update Priority",
                    key=f"update_priority_{ticket['ticket_id']}",
                    use_container_width=True,
                ):
                    if update_ticket_priority(
                        ticket["ticket_id"],
                        new_priority,
                    ):
                        st.success("Priority updated.")
                        st.rerun()

            with col_status:
                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(current_status),
                    key=f"status_{ticket['ticket_id']}",
                )

                if st.button(
                    "Update Status",
                    key=f"update_status_{ticket['ticket_id']}",
                    use_container_width=True,
                ):
                    if update_ticket_status(
                        ticket["ticket_id"],
                        new_status,
                    ):
                        st.success("Status updated.")
                        st.rerun()


            st.divider()
            st.markdown("**Ticket Escalation**")

            if ticket["is_escalated"]:
                st.warning("This ticket is escalated.")

                if st.button(
                    "Remove Escalation",
                    key=f"remove_escalation_{ticket['ticket_id']}",
                    use_container_width=True,
                ):
                    if update_ticket_escalation(
                        ticket["ticket_id"],
                        False,
                    ):
                        st.success("Escalation removed.")
                        st.rerun()

            else:
                if st.button(
                    "Escalate Ticket",
                    key=f"escalate_{ticket['ticket_id']}",
                    use_container_width=True,
                ):
                    if update_ticket_escalation(
                        ticket["ticket_id"],
                        True,
                    ):
                        st.success("Ticket escalated successfully.")
                        st.rerun()


            st.divider()
            st.markdown("**Resolution Notes**")

            resolution_notes = st.text_area(
                "Record how this issue was resolved",
                value=ticket["resolution_notes"] or "",
                key=f"resolution_notes_{ticket['ticket_id']}",
                placeholder="Describe the solution or action taken...",
            )

            if st.button(
                "Save Resolution Notes",
                key=f"save_notes_{ticket['ticket_id']}",
                use_container_width=True,
            ):
                try:
                    success = update_ticket_resolution_notes(
                        ticket["ticket_id"],
                        resolution_notes,
                    )

                    if success:
                        st.success("Resolution notes saved.")
                        st.rerun()
                    else:
                        st.error("Ticket not found.")

                except ValueError as error:
                    st.error(str(error))

def show_agent_dashboard(staff):
    """Display tickets assigned to the logged-in support agent."""

    agent_id = staff["id"]
    tickets = get_agent_tickets(agent_id)

    st.title("Support Agent Workspace")
    st.caption(f"Welcome, {staff['name']}")

    total = len(tickets)
    open_count = sum(t["status"] == "Open" for t in tickets)
    progress_count = sum(t["status"] == "In Progress" for t in tickets)
    resolved_count = sum(t["status"] == "Resolved" for t in tickets)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Assigned Tickets", total)
    col2.metric("Open", open_count)
    col3.metric("In Progress", progress_count)
    col4.metric("Resolved", resolved_count)

    st.divider()
    st.subheader("My Assigned Tickets")

    if not tickets:
        st.info("You currently have no assigned tickets.")
        return

    for ticket in tickets:
        with st.container(border=True):
            st.markdown(f"### {ticket['ticket_id']}")
            st.write(ticket["issue"])

            st.caption(f"Customer: {ticket['customer_name'] or 'Unknown'}")
            st.caption(f"Email: {ticket['customer_email'] or 'Not available'}")

            col1, col2, col3 = st.columns(3)

            col1.write(f"**Status:** {ticket['status']}")
            col2.write(f"**Priority:** {ticket['priority']}")
            col3.write(
                f"**Escalated:** {'Yes' if ticket['is_escalated'] else 'No'}"
            )

            st.caption(f"Created: {ticket['created_at']}")

            if ticket["resolution_notes"]:
                st.info(f"Resolution notes: {ticket['resolution_notes']}")

            st.divider()
            st.markdown("**Update Ticket Status**")

            if ticket["status"] == "Resolved":
                st.success("This ticket has been resolved.")
                st.caption("Only an administrator can reopen it.")

            else:
                agent_status_options = ["In Progress", "Resolved"]

                new_agent_status = st.selectbox(
                    "Status",
                    agent_status_options,
                    index=(
                        agent_status_options.index(ticket["status"])
                        if ticket["status"] in agent_status_options
                        else 0
                    ),
                    key=f"agent_status_{ticket['ticket_id']}",
                )

                if st.button(
                    "Update Status",
                    key=f"agent_update_status_{ticket['ticket_id']}",
                    use_container_width=True,
                ):
                    try:
                        success = update_agent_ticket_status(
                            ticket["ticket_id"],
                            agent_id,
                            new_agent_status,
                        )

                        if success:
                            st.success("Ticket status updated.")
                            st.rerun()
                        else:
                            st.error("Unable to update ticket status.")

                    except (ValueError, PermissionError) as error:
                        st.error(str(error))


            st.divider()
            st.markdown("**Customer Conversation**")

            replies = get_ticket_replies(ticket["ticket_id"])

            if not replies:
                st.caption("No replies yet.")

            for reply in replies:
                sender = reply["sender_name"] or reply["sender_role"].title()

                with st.chat_message(
                    "assistant" if reply["sender_role"] == "agent" else "user"
                ):
                    st.caption(
                        f"{sender} | {reply['created_at']}"
                    )
                    st.write(reply["message"])

            agent_reply = st.text_area(
                "Write a reply to the customer",
                key=f"agent_reply_{ticket['ticket_id']}",
                placeholder="Type your response...",
            )

            if st.button(
                "Send Reply",
                key=f"send_reply_{ticket['ticket_id']}",
                use_container_width=True,
            ):
                try:
                    add_ticket_reply(
                        ticket["ticket_id"],
                        "agent",
                        agent_id,
                        agent_reply,
                    )

                    st.success("Reply sent successfully.")
                    st.rerun()

                except (ValueError, PermissionError) as error:
                    st.error(str(error))
