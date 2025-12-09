from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.core.utils import get_default_image_url

from .factories import AttributeFactory
from .factories import AttributeValueFactory
from .factories import CategoryFactory
from .factories import ProductAttributeFactory
from .factories import ProductFactory
from .factories import ProductVariantFactory

pytestmark = pytest.mark.django_db


# -----------------------------------------------------------------------------
# Category Model Tests
# -----------------------------------------------------------------------------
def test_category_str_returns_name():
    category = CategoryFactory(name="Electronics")
    assert str(category) == "Electronics"


def test_category_get_image_url_returns_default_when_no_image():
    category = CategoryFactory()
    assert category.get_image_url() == get_default_image_url()


# -----------------------------------------------------------------------------
# Attribute Model Tests
# -----------------------------------------------------------------------------
def test_attribute_str_returns_name():
    attribute = AttributeFactory(name="Color")
    assert str(attribute) == "Color"


# -----------------------------------------------------------------------------
# AttributeValue Model Tests
# -----------------------------------------------------------------------------
def test_attribute_value_must_be_unique_per_attribute_case_insensitive():
    attribute = AttributeFactory(name="Material")
    AttributeValueFactory(attribute=attribute, value="Cotton")
    with pytest.raises(IntegrityError):
        AttributeValueFactory(attribute=attribute, value="cotton")


def test_attribute_value_can_be_repeated_in_different_attributes():
    attribute1 = AttributeFactory(name="Size")
    attribute2 = AttributeFactory(name="Fit")
    value1 = AttributeValueFactory(attribute=attribute1, value="Large")
    value2 = AttributeValueFactory(attribute=attribute2, value="Large")
    assert value1.value == value2.value
    assert value1.attribute != value2.attribute


def test_attribute_value_str_includes_attribute_and_value():
    attribute = AttributeFactory(name="Size")
    attribute_value = AttributeValueFactory(attribute=attribute, value="Large")
    assert str(attribute_value) == "Size: Large"


# -----------------------------------------------------------------------------
# Product Model Tests
# -----------------------------------------------------------------------------
def test_product_name_must_be_unique_per_category_case_insensitive():
    category = CategoryFactory(name="Furniture")
    ProductFactory(category=category, name="Office Chair")
    with pytest.raises(IntegrityError):
        ProductFactory(category=category, name="office chair")


def test_product_name_can_be_repeated_in_different_categories():
    category1 = CategoryFactory(name="Clothing")
    category2 = CategoryFactory(name="Accessories")
    product1 = ProductFactory(category=category1, name="Sunglasses")
    product2 = ProductFactory(category=category2, name="Sunglasses")
    assert product1.name == product2.name
    assert product1.category != product2.category


def test_product_str_returns_name():
    product = ProductFactory(name="4K Television")
    assert str(product) == "4K Television"


# -----------------------------------------------------------------------------
# ProductAttribute Model Tests
# -----------------------------------------------------------------------------
def test_product_attribute_must_be_unique_per_product_and_attribute():
    product = ProductFactory(name="Laptop")
    attribute = AttributeFactory(name="Processor")
    ProductAttributeFactory(product=product, attribute=attribute)
    with pytest.raises(IntegrityError):
        ProductAttributeFactory(product=product, attribute=attribute)


def test_product_attribute_str_includes_product_and_attribute():
    product = ProductFactory(name="Smartphone")
    attribute = AttributeFactory(name="Battery Life")
    product_attribute = ProductAttributeFactory(product=product, attribute=attribute)
    assert str(product_attribute) == "Smartphone - Battery Life"


# -----------------------------------------------------------------------------
# ProductVariant Model Tests
# -----------------------------------------------------------------------------
def test_product_variant_str_includes_product_name_and_sku():
    product = ProductFactory(name="Gaming Laptop")
    variant = ProductVariantFactory(product=product, sku="GL-001")
    assert str(variant) == "Gaming Laptop (GL-001)"


def test_product_variant_price_returns_base_price_if_no_override():
    product = ProductFactory(base_price=Decimal("199.99"))
    variant = ProductVariantFactory(product=product, price_override=None)
    assert variant.price == Decimal("199.99")


def test_product_variant_price_returns_override_if_set():
    product = ProductFactory(base_price=Decimal("199.99"))
    variant = ProductVariantFactory(product=product, price_override=Decimal("99.99"))
    assert variant.price == Decimal("99.99")
