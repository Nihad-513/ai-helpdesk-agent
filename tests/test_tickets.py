
from database import create_support_ticket

ticket_id = create_support_ticket(
    issue="Customer wants to know whether international shipping is available.",
    customer_name="Test Customer",
    customer_email="test@example.com",
)

print("Support ticket created successfully!")
print("Ticket ID:", ticket_id)
