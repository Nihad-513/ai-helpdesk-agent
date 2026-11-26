
from database import get_support_ticket, update_ticket_status

ticket_id = input("Enter your ticket ID: ").strip()

updated = update_ticket_status(ticket_id, "In Progress")

if updated:
    ticket = get_support_ticket(ticket_id)
    print("\nTicket updated successfully!")
    print("Ticket ID:", ticket["ticket_id"])
    print("New status:", ticket["status"])
else:
    print("Ticket not found.")
