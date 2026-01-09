import pytest
from django.db import IntegrityError

from apps.cart.choices import CartStatus
from apps.products.tests.factories import ProductVariantFactory
from apps.users.tests.factories import UserFactory

from .factories import CartFactory
from .factories import CartItemFactory


@pytest.mark.django_db
class TestCartModel:
    def test_str_method_for_authenticated_user(self):
        cart = CartFactory()
        expected_str = f"Cart {cart.pk} for user {cart.user} ({cart.status})"
        assert str(cart) == expected_str

    def test_str_method_for_anonymous_user(self):
        cart = CartFactory(is_anonymous=True)
        expected_str = f"Cart {cart.pk} for session {cart.session_key} ({cart.status})"
        assert str(cart) == expected_str

    def test_constraint_unique_open_cart_per_user(self):
        user = UserFactory()
        CartFactory(user=user, session_key="", status=CartStatus.OPEN)
        with pytest.raises(IntegrityError):
            CartFactory(user=user, session_key="", status=CartStatus.OPEN)

    def test_constraint_unique_open_cart_per_session(self):
        session_key = "unique-session-key"
        CartFactory(user=None, session_key=session_key, status=CartStatus.OPEN)
        with pytest.raises(IntegrityError):
            CartFactory(user=None, session_key=session_key, status=CartStatus.OPEN)

    def test_constraint_cart_requires_user_or_session_key(self):
        with pytest.raises(IntegrityError):
            CartFactory(user=None, session_key="")

    def test_post_generation_items(self):
        cart = CartFactory(items=[{"quantity": 2}, {"quantity": 3}])
        assert cart.items.count() == 2  # noqa: PLR2004
        quantities = [item.quantity for item in cart.items.all()]
        assert sorted(quantities) == [2, 3]


@pytest.mark.django_db
class TestCartItemModel:
    def test_str_method(self):
        cart = CartFactory()
        variant = ProductVariantFactory()
        cart_item = CartItemFactory(cart=cart, variant=variant, quantity=2)
        expected_str = f"{cart_item.cart_id} - {variant.sku} x 2"
        assert str(cart_item) == expected_str

    def test_constraint_unique_variant_per_cart(self):
        cart = CartFactory()
        variant = ProductVariantFactory()
        CartItemFactory(cart=cart, variant=variant)
        with pytest.raises(IntegrityError):
            CartItemFactory(cart=cart, variant=variant)

    def test_property_line_total(self):
        variant = ProductVariantFactory(price=50.00)
        cart_item = CartItemFactory(variant=variant, quantity=3)
        assert cart_item.line_total == 150.00  # noqa: PLR2004

    def test_same_variant_different_carts(self):
        variant = ProductVariantFactory()
        item1 = CartItemFactory(variant=variant)
        item2 = CartItemFactory(variant=variant)
        assert item1.variant == item2.variant
        assert item1.cart != item2.cart
