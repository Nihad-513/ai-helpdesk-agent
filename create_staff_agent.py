
"""Create a Bean & Brew support agent."""

from getpass import getpass
from database import create_staff_account

name = input("Agent name: ").strip()
email = input("Agent email: ").strip()

password = getpass("Create password: ")
confirm_password = getpass("Confirm password: ")

if password != confirm_password:
    print("Passwords do not match.")
else:
    try:
        agent_id = create_staff_account(
            name=name,
            email=email,
            password=password,
            role="agent",
        )

        print(f"Agent created successfully. ID: {agent_id}")

    except ValueError as error:
        print(f"Error: {error}")
