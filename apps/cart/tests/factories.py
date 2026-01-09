from factory import Faker
from factory import Sequence
from factory import SubFactory
from factory import Trait
from factory import post_generation
from factory.django import DjangoModelFactory

from apps.cart.choices import CartStatus
from apps.cart.models import Cart
from apps.cart.models import CartItem
from apps.products.tests.factories import ProductVariantFactory
from apps.users.tests.factories import UserFactory


class CartFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    session_key = None
    status = CartStatus.OPEN

    class Meta:
        model = Cart
        skip_postgeneration_save = True

    class Params:
        is_anonymous = Trait(
            user=None,
            session_key=Sequence(lambda n: f"session-{n:032d}"[:40]),
        )
        is_checked_out = Trait(status=CartStatus.CHECKED_OUT)
        is_abandoned = Trait(status=CartStatus.ABANDONED)

    @post_generation
    def items(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        if isinstance(extracted, int):
            for _ in range(extracted):
                CartItemFactory(cart=self)
            return

        for item in extracted:
            if isinstance(item, dict):
                CartItemFactory(cart=self, **item)
            else:
                CartItemFactory(cart=self, variant=item)


class CartItemFactory(DjangoModelFactory):
    cart = SubFactory(CartFactory)
    variant = SubFactory(ProductVariantFactory)
    quantity = Faker("random_int", min=1, max=5)

    class Meta:
        model = CartItem
