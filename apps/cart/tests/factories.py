from factory import Faker
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
    session_key = ""
    status = CartStatus.OPEN

    class Meta:
        model = Cart
        skip_postgeneration_save = True

    class Params:
        is_anonymous = Trait(user=None, session_key=Faker("md5"))
        is_checked_out = Trait(status=CartStatus.CHECKED_OUT)
        is_abandoned = Trait(status=CartStatus.ABANDONED)

    @post_generation
    def items(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for item in extracted:
            CartItemFactory(cart=self, **item)


class CartItemFactory(DjangoModelFactory):
    cart = SubFactory(CartFactory)
    variant = SubFactory(ProductVariantFactory)
    quantity = Faker("random_int", min=1, max=5)

    class Meta:
        model = CartItem
