
import pytest

from database import (
    register_customer,
    authenticate_customer,
    get_customer_by_email,
)


def test_customer_registration():
    customer_id = register_customer(
        name="Test Customer",
        email="auth_test@beanbrew.com",
        password="TestPassword123",
    )

    assert customer_id is not None

    customer = get_customer_by_email("auth_test@beanbrew.com")

    assert customer is not None
    assert customer["name"] == "Test Customer"
    assert customer["email"] == "auth_test@beanbrew.com"


def test_customer_login_with_correct_password():
    register_customer(
        name="Test Customer",
        email="login_test@beanbrew.com",
        password="TestPassword123",
    )

    customer = authenticate_customer(
        "login_test@beanbrew.com",
        "TestPassword123",
    )

    assert customer is not None
    assert customer["email"] == "login_test@beanbrew.com"


def test_customer_login_rejects_wrong_password():
    register_customer(
        name="Test Customer",
        email="wrong_password@beanbrew.com",
        password="TestPassword123",
    )

    customer = authenticate_customer(
        "wrong_password@beanbrew.com",
        "WrongPassword123",
    )

    assert customer is None


def test_duplicate_customer_registration_is_rejected():
    register_customer(
        name="Test Customer",
        email="duplicate@beanbrew.com",
        password="TestPassword123",
    )

    with pytest.raises(ValueError):
        register_customer(
            name="Another Customer",
            email="duplicate@beanbrew.com",
            password="TestPassword123",
        )


def test_customer_lookup_does_not_expose_password_hash():
    register_customer(
        name="Test Customer",
        email="lookup@beanbrew.com",
        password="TestPassword123",
    )

    customer = get_customer_by_email("lookup@beanbrew.com")

    assert customer is not None
    assert "password_hash" not in customer
