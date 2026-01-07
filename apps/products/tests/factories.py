from django.utils.text import slugify
from factory import Faker
from factory import Iterator
from factory import LazyAttribute
from factory import Sequence
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.django import ImageField

from apps.products.choices import AttributeGroup
from apps.products.models import Attribute
from apps.products.models import AttributeValue
from apps.products.models import Category
from apps.products.models import Product
from apps.products.models import ProductImage
from apps.products.models import ProductVariant
from apps.products.models import ProductVariantAttributeValue


class CategoryFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Category {n}")
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    description = Faker("paragraph")
    image = ImageField(filename="category.jpg")
    is_active = True

    class Meta:
        model = Category


class AttributeFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Attribute {n}")
    group = Iterator([choice[0] for choice in AttributeGroup.choices])
    description = Faker("paragraph")

    class Meta:
        model = Attribute
        skip_postgeneration_save = True

    @post_generation
    def values(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for value in extracted:
            AttributeValueFactory(attribute=self, value=value)


class AttributeValueFactory(DjangoModelFactory):
    attribute = SubFactory(AttributeFactory)
    value = Sequence(lambda n: f"Value {n}")
    sort_order = None

    class Meta:
        model = AttributeValue


class ProductFactory(DjangoModelFactory):
    category = SubFactory(CategoryFactory)
    name = Sequence(lambda n: f"Product {n}")
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    short_description = Faker("sentence")
    full_description = Faker("paragraph")
    is_active = True

    class Meta:
        model = Product
        skip_postgeneration_save = True

    @post_generation
    def attributes(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.attributes.add(*extracted)


class ProductVariantFactory(DjangoModelFactory):
    product = SubFactory(ProductFactory)
    sku = Sequence(lambda n: f"SKU-{n:05d}")
    price = Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    stock_quantity = Faker("pyint", min_value=0, max_value=100)
    sort_order = None
    is_active = True

    class Meta:
        model = ProductVariant
        skip_postgeneration_save = True

    @post_generation
    def attribute_values(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for attribute_value in extracted:
            ProductVariantAttributeValueFactory(
                product_variant=self,
                attribute_value=attribute_value,
            )


class ProductVariantAttributeValueFactory(DjangoModelFactory):
    product_variant = SubFactory(ProductVariantFactory)
    attribute_value = SubFactory(AttributeValueFactory)

    class Meta:
        model = ProductVariantAttributeValue

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        product_variant = kwargs.get("product_variant")
        attribute_value = kwargs.get("attribute_value")
        if product_variant is not None and attribute_value is not None:
            product = product_variant.product
            if product and product.pk:
                product.attributes.add(attribute_value.attribute)
        return super()._create(model_class, *args, **kwargs)


class ProductImageFactory(DjangoModelFactory):
    product = SubFactory(ProductFactory)
    variant = None
    image = ImageField(filename="test.jpg")
    alt_text = ""
    sort_order = None
    is_active = True

    class Meta:
        model = ProductImage
