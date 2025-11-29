import stripe
from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(course):
    """Создает продукт в страйпе"""
    if course.stripe_product_id:
        return course.stripe_product_id

    product = stripe.Product.create(name=course.name)
    course.stripe_product_id = product.id
    course.save(update_fields=["stripe_product_id"])
    return product.id


def create_stripe_price(course, amount):
    """Создает цену в страйпе"""
    if course.stripe_price_id:
        return course.stripe_price_id

    product_id = create_stripe_product(course)

    price = stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),
        product=product_id,
    )
    course.stripe_price_id = price.id
    course.save(update_fields=["stripe_price_id"])
    return price.id


def create_stripe_session(price_id):
    """Создает сессию в страйпе"""

    session = stripe.checkout.Session.create(
        success_url="https://127.0.0.1:8000/",
        cancel_url="http://localhost:8000/",
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="payment",
    )
    return session.id, session.url
