
"""Bean & Brew customer dashboard."""

import streamlit as st
from app.chat import show_chat
from database import (
    get_customer_tickets,
    get_customer_ticket_replies,
    add_ticket_reply,
)

def navigate_to_page(page):
    """Navigate to another dashboard page."""
    st.session_state.dashboard_page = page


def show_dashboard(customer):
    """Display the authenticated customer's dashboard."""

    customer_id = customer["id"]
    tickets = get_customer_tickets(customer_id)

    # Sidebar navigation
    with st.sidebar:
        st.markdown("## ♨ Bean & Brew")
        st.caption("Customer Portal")
        st.divider()

        page = st.radio(
            "Navigation",
            ["Overview", "AI Support Chat", "My Tickets", "My Account"],
            label_visibility="collapsed",
            key="dashboard_page",
        )

        st.divider()
        st.write(f"Signed in as **{customer['name']}**")

        if st.button("Sign out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.customer = None
            st.session_state.staff_authenticated = False
            st.session_state.staff = None
            st.rerun()

    # Common ticket statistics
    total_tickets = len(tickets)
    open_tickets = sum(
        ticket["status"] == "Open" for ticket in tickets
    )
    resolved_tickets = sum(
        ticket["status"] == "Resolved" for ticket in tickets
    )

    # --------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------

    if page == "Overview":

        st.markdown(
            f"""
            <div class="welcome-card">
                <h1>Welcome, {customer['name']}!</h1>
                <p>How can we make your Bean & Brew experience better today?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h2 class="section-title">Your support overview</h2>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Tickets", total_tickets)

        with col2:
            st.metric("Open Tickets", open_tickets)

        with col3:
            st.metric("Resolved Tickets", resolved_tickets)

        st.divider()

        st.markdown("### What would you like to do?")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("### 💬 AI Support Assistant")
                st.write(
                    "Get instant answers to questions about "
                    "orders, payments, shipping and store policies."
                )
                st.button(
                 "Open AI Support Chat",
                 use_container_width=True,
                 on_click=navigate_to_page,
                 args=("AI Support Chat",),
                )

        with col2:
            with st.container(border=True):
                st.markdown("### 🎫 Support Tickets")
                st.write(
                    "Review your previous support requests "
                    "and track their progress."
                )

                if  st.button(
                    "View my tickets",
                    use_container_width=True,
                    on_click=navigate_to_page,
                    args=("My Tickets",),
                    ):
                    st.session_state.dashboard_page = "My Tickets"
                    st.rerun()

        st.divider()

        st.markdown("### Recent support activity")

        if tickets:
            for ticket in tickets[:3]:
                with st.container(border=True):
                    st.markdown(f"**{ticket['ticket_id']}**")
                    st.write(ticket["issue"])
                    st.caption(
                        f"Status: {ticket['status']} · "
                        f"Created: {ticket['created_at']}"
                    )
        else:
            st.info(
                "You haven't created any support tickets yet."
            )

    # --------------------------------------------------
    # MY TICKETS
    # --------------------------------------------------
    # AI SUPPORT CHAT
    elif page == "AI Support Chat":
        show_chat(customer)

    elif page == "My Tickets":

        st.title("My Support Tickets")
        st.caption(
            "View and track your customer support requests."
        )

        if not tickets:
            st.info(
                "No support tickets found. "
                "Contact our AI assistant if you need help."
            )

        else:
            for ticket in tickets:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(
                            f"### {ticket['ticket_id']}"
                        )
                        st.write(ticket["issue"])
                        st.caption(
                            f"Created: {ticket['created_at']}"
                        )

                    with col2:
                        status = ticket["status"]

                        if status == "Resolved":
                            st.success(status)
                        elif status == "In Progress":
                            st.info(status)
                        else:
                            st.warning(status)

                    st.divider()
                    st.markdown("**Conversation with Support**")

                    replies = get_customer_ticket_replies(
                        ticket["ticket_id"],
                        customer_id,
                    )

                    if not replies:
                        st.caption("No replies yet. Our support team will respond soon.")

                    for reply in replies:
                        sender = reply["sender_name"] or reply["sender_role"].title()

                        with st.chat_message(
                            "assistant" if reply["sender_role"] == "agent" else "user"
                        ):
                            st.caption(
                                f"{sender} | {reply['created_at']}"
                            )
                            st.write(reply["message"])

                    customer_reply = st.text_area(
                        "Write a reply",
                        key=f"customer_reply_{ticket['ticket_id']}",
                        placeholder="Type your message to our support team...",
                    )

                    if st.button(
                        "Send Reply",
                        key=f"customer_send_reply_{ticket['ticket_id']}",
                        use_container_width=True,
                    ):
                        try:
                            add_ticket_reply(
                                ticket["ticket_id"],
                                "customer",
                                customer_id,
                                customer_reply,
                            )

                            st.success("Your reply has been sent.")
                            st.rerun()

                        except (ValueError, PermissionError) as error:
                            st.error(str(error))


    # --------------------------------------------------
    # MY ACCOUNT
    # --------------------------------------------------

    elif page == "My Account":

        st.title("My Account")
        st.caption("Your Bean & Brew account information.")

        with st.container(border=True):
            st.markdown("### Personal Information")

            st.text_input(
                "Full name",
                value=customer["name"],
                disabled=True,
            )

            st.text_input(
                "Email address",
                value=customer["email"],
                disabled=True,
            )

            st.text_input(
                "Customer ID",
                value=str(customer["id"]),
                disabled=True,
            )

        st.divider()

        st.markdown("### Account Summary")
        st.write(f"Total support tickets: **{total_tickets}**")
        st.write(f"Resolved tickets: **{resolved_tickets}**")
