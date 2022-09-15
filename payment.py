import stripe
from flask import abort

stripe.api_key = "sk_test_51HcbGpJcNvQIxoIBFyKciKyQHwjyOmlgJYYFUVgvVzc3HfLy8NHviHQxagxAVxAdODoKnHO4KLTiDUHjkmETcD0P00VyDzElzF"


def createCustomer(
    email: str,
    given_name: str,
    family_name: str,
    phone,
    postcode: str,
    uprn: int,
    over16: bool,
    restricted: bool,
):
    # Customer object
    customer = {
        "address": {
            "postal_code": postcode,
        },
        "email": email,
        "name": given_name.capitalize() + " " + family_name.capitalize(),
        "phone": phone,
        "metadata": {
            "jf:uprn": uprn,
            "source": "join-form",
            "jf:over16": str(over16),
            "jf:restricted": str(restricted),
            "jf:name": "|".join((given_name, family_name)),
        },
    }

    return stripe.Customer.create(**customer)


def createPayment(
    amount: int, customer_id: str, description="first_membership_payment"
):
    if (amount > 2000 and description == "first_membership_payment") or amount < 100:
        abort(400)

    return stripe.PaymentIntent.create(
        amount=amount,
        currency="gbp",
        automatic_payment_methods={
            "enabled": True,
        },
        customer_id=customer_id,
        description=description,
        setup_future_usage="off_session",
    )
