from decimal import Decimal

from factory import Faker
from factory import Sequence
from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.products.models import Attribute
from apps.products.models import AttributeValue
from apps.products.models import Category
from apps.products.models import Product
from apps.products.models import ProductAttribute
from apps.products.models import ProductVariant


class CategoryFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"category-{n}")
    slug = Sequence(lambda n: f"category-{n}")
    description = Faker("paragraph")
    is_active = True

    class Meta:
        model = Category


class AttributeFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"attribute-{n}")
    description = Faker("paragraph")
    is_active = True

    class Meta:
        model = Attribute


class AttributeValueFactory(DjangoModelFactory):
    attribute = SubFactory(AttributeFactory)
    value = Faker("word")
    sort_order = 0
    is_active = True

    class Meta:
        model = AttributeValue


class ProductFactory(DjangoModelFactory):
    category = SubFactory(CategoryFactory)
    name = Faker("word")
    slug = Sequence(lambda n: f"product-{n}")
    short_description = Faker("sentence")
    full_description = Faker("paragraph")
    base_price = Decimal("9.99")
    is_active = True

    class Meta:
        model = Product


class ProductAttributeFactory(DjangoModelFactory):
    product = SubFactory(ProductFactory)
    attribute = SubFactory(AttributeFactory)

    class Meta:
        model = ProductAttribute


class ProductVariantFactory(DjangoModelFactory):
    product = SubFactory(ProductFactory)
    sku = Sequence(lambda n: f"SKU-{n}")
    price_override = None
    stock_quantity = 0
    sort_order = 0
    is_active = True

    class Meta:
        model = ProductVariant
