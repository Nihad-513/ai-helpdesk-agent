
from database import (
    init_db,
    register_customer,
    authenticate_customer,
    get_customer_by_email,
)

init_db()

test_email = "auth_test@beanbrew.com"
test_password = "TestPassword123"

print("\nTesting customer registration:")

try:
    customer_id = register_customer(
        name="Test Customer",
        email=test_email,
        password=test_password,
    )
    print("Registration successful!")
    print("Customer ID:", customer_id)

except ValueError as exc:
    print("Registration:", exc)


print("\nTesting customer login:")

customer = authenticate_customer(
    test_email,
    test_password,
)

print("Login successful!" if customer else "Login failed!")
print("Customer:", customer)


print("\nTesting incorrect password:")

wrong_login = authenticate_customer(
    test_email,
    "WrongPassword123",
)

print("Rejected successfully!" if wrong_login is None else "Unexpected login!")


print("\nTesting duplicate registration:")

try:
    register_customer(
        name="Another Customer",
        email=test_email,
        password=test_password,
    )
    print("Unexpected duplicate registration!")

except ValueError as exc:
    print("Duplicate prevented:", exc)


print("\nTesting customer lookup:")

print(get_customer_by_email(test_email))
