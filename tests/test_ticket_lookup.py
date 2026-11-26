
from database import get_support_ticket

ticket_id = input("Enter your ticket ID: ").strip()

ticket = get_support_ticket(ticket_id)

if ticket:
    print("\nTicket found!")
    print("Ticket ID:", ticket["ticket_id"])
    print("Customer:", ticket["customer_name"])
    print("Email:", ticket["customer_email"])
    print("Issue:", ticket["issue"])
    print("Status:", ticket["status"])
    print("Created:", ticket["created_at"])
else:
    print("Ticket not found.")
