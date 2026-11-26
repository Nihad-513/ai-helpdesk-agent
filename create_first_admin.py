
"""Securely create the first Bean & Brew administrator."""

from getpass import getpass

from database import create_staff_account, get_connection


def main():
    # Prevent creating another initial administrator.
    with get_connection() as connection:
        admin_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM staff_accounts
            WHERE role = 'admin'
            """
        ).fetchone()[0]

    if admin_count > 0:
        print("An administrator account already exists.")
        print("Use the existing admin account to manage staff.")
        return

    print("\n=== Bean & Brew: Initial Admin Setup ===\n")

    name = input("Administrator name: ").strip()
    email = input("Administrator email: ").strip()

    password = getpass("Create password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    try:
        admin_id = create_staff_account(
            name=name,
            email=email,
            password=password,
            role="admin",
        )

        print("\nAdministrator account created successfully.")
        print(f"Admin ID: {admin_id}")
        print(f"Email: {email}")

    except ValueError as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
