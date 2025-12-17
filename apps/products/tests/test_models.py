from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.core.utils import get_default_image_url

from .factories import AttributeFactory
from .factories import AttributeValueFactory
from .factories import CategoryFactory
from .factories import ProductFactory
from .factories import ProductImageFactory
from .factories import ProductVariantAttributeValueFactory
from .factories import ProductVariantFactory


@pytest.mark.django_db
class TestCategory:
    def test_str_method_returns_name(self):
        category = CategoryFactory(name="Electronics")
        assert str(category) == "Electronics"

    def test_name_is_unique_case_insensitive(self):
        CategoryFactory(name="Books", slug="books")
        with pytest.raises(IntegrityError):
            CategoryFactory(name="books", slug="books-1")

    def test_slug_is_unique(self):
        CategoryFactory(slug="home-appliances")
        with pytest.raises(IntegrityError):
            CategoryFactory(slug="home-appliances")

    def test_get_image_url_method_returns_default_when_no_image(self):
        category = CategoryFactory(image="")
        assert category.get_image_url() == get_default_image_url()


@pytest.mark.django_db
class TestAttribute:
    def test_str_method_returns_name(self):
        attribute = AttributeFactory(name="Color")
        assert str(attribute) == "Color"

    def test_name_is_unique_case_insensitive(self):
        AttributeFactory(name="Material")
        with pytest.raises(IntegrityError):
            AttributeFactory(name="material")

    def test_factory_post_generation_values_creates_attribute_values(self):
        attribute = AttributeFactory(values=["Red", "Blue", "Green"])
        values = list(attribute.values.values_list("value", flat=True))
        assert set(values) == {"Red", "Blue", "Green"}
        assert attribute.values.count() == 3  # noqa: PLR2004


@pytest.mark.django_db
class TestAttributeValue:
    def test_str_method_returns_attribute_name_and_value(self):
        attribute = AttributeFactory(name="Size")
        attribute_value = AttributeValueFactory(attribute=attribute, value="Large")
        assert str(attribute_value) == "Size: Large"

    def test_value_is_unique_per_attribute_case_insensitive(self):
        attribute = AttributeFactory(name="Color")
        AttributeValueFactory(attribute=attribute, value="Red")
        with pytest.raises(IntegrityError):
            AttributeValueFactory(attribute=attribute, value="red")

    def test_same_value_allowed_for_different_attributes(self):
        attribute1 = AttributeFactory(name="Color")
        attribute2 = AttributeFactory(name="Material")
        value1 = AttributeValueFactory(attribute=attribute1, value="Red")
        value2 = AttributeValueFactory(attribute=attribute2, value="Red")
        assert value1.value == value2.value
        assert value1.attribute != value2.attribute


@pytest.mark.django_db
class TestProduct:
    def test_str_method_returns_name(self):
        product = ProductFactory(name="Smartphone")
        assert str(product) == "Smartphone"

    def test_name_is_unique_per_category_case_insensitive(self):
        category = CategoryFactory()
        ProductFactory(category=category, name="Tablet", slug="tablet")
        with pytest.raises(IntegrityError):
            ProductFactory(category=category, name="tablet", slug="tablet-1")

    def test_same_name_allowed_in_different_categories(self):
        category1 = CategoryFactory(name="Furniture")
        category2 = CategoryFactory(name="Office Supplies")
        product1 = ProductFactory(category=category1, name="Desk", slug="desk")
        product2 = ProductFactory(category=category2, name="Desk", slug="desk-1")
        assert product1.name == product2.name
        assert product1.category != product2.category

    def test_slug_is_unique(self):
        ProductFactory(slug="gaming-laptop")
        with pytest.raises(IntegrityError):
            ProductFactory(slug="gaming-laptop")

    def test_factory_post_generation_attributes_creates_product_attributes(self):
        attribute1 = AttributeFactory(name="Warranty")
        attribute2 = AttributeFactory(name="Battery Life")
        product = ProductFactory(attributes=[attribute1, attribute2])
        attributes = list(product.attributes.all())
        assert set(attributes) == {attribute1, attribute2}
        assert product.attributes.count() == 2  # noqa: PLR2004


@pytest.mark.django_db
class TestProductVariant:
    def test_str_method_returns_product_name_and_variant_sku(self):
        product = ProductFactory(name="Camera")
        variant = ProductVariantFactory(product=product, sku="CAM-001")
        assert str(variant) == "Camera (SKU: CAM-001)"

    def test_unique_sku(self):
        ProductVariantFactory(sku="UNIQUE-SKU")
        with pytest.raises(IntegrityError):
            ProductVariantFactory(sku="UNIQUE-SKU")

    def test_price_property_returns_correct_value(self):
        product = ProductFactory(base_price=Decimal("100.00"))
        variant_with_price_override = ProductVariantFactory(
            product=product,
            price_override=Decimal("80.00"),
        )
        variant_without_price_override = ProductVariantFactory(
            product=product,
            price_override=None,
        )
        assert variant_with_price_override.price == Decimal("80.00")
        assert variant_without_price_override.price == Decimal("100.00")

    def test_factory_post_generation_attribute_values_creates_attribute_values(self):
        attribute1 = AttributeFactory(name="Color")
        value1 = AttributeValueFactory(attribute=attribute1, value="Black")
        attribute2 = AttributeFactory(name="Size")
        value2 = AttributeValueFactory(attribute=attribute2, value="Medium")
        product = ProductFactory(attributes=[attribute1, attribute2])
        variant = ProductVariantFactory(
            product=product,
            attribute_values=[value1, value2],
        )
        linked_values = list(variant.attribute_values.all())
        assert set(linked_values) == {value1, value2}
        assert variant.attribute_values.count() == 2  # noqa: PLR2004


@pytest.mark.django_db
class TestProductVariantAttributeValue:
    def test_str_method_returns_product_variant_sku_and_attribute_value(self):
        attribute = AttributeFactory(name="Color")
        attribute_value = AttributeValueFactory(attribute=attribute, value="Red")
        product = ProductFactory(attributes=[attribute])
        variant = ProductVariantFactory(product=product, sku="VAR-001")
        link = ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=attribute_value,
        )
        assert str(link) == "VAR-001 - Color: Red"

    def test_save_method_sets_attribute_from_attribute_value(self):
        attribute = AttributeFactory(name="Color")
        value = AttributeValueFactory(attribute=attribute, value="Blue")
        product = ProductFactory(attributes=[attribute])
        variant = ProductVariantFactory(product=product)
        link = ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=value,
        )
        link.refresh_from_db()
        assert link.attribute_id == attribute.id

    def test_unique_value_per_attribute_per_variant(self):
        attribute = AttributeFactory(name="Size")
        value1 = AttributeValueFactory(attribute=attribute, value="Medium")
        value2 = AttributeValueFactory(attribute=attribute, value="Large")
        product = ProductFactory(attributes=[attribute])
        variant = ProductVariantFactory(product=product)
        ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=value1,
        )
        link_invalid = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=value2,
        )
        with pytest.raises(ValidationError):
            link_invalid.save()

    def test_attribute_must_belong_to_product(self):
        attribute = AttributeFactory(name="Material")
        value = AttributeValueFactory(attribute=attribute, value="Cotton")
        product = ProductFactory()
        variant = ProductVariantFactory(product=product)
        link = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=value,
        )
        with pytest.raises(ValidationError):
            link.save()

    def test_duplicate_variant_attribute_value_pair_raises_validation_error(self):
        attribute = AttributeFactory(name="Size")
        value = AttributeValueFactory(attribute=attribute, value="Small")
        product = ProductFactory(attributes=[attribute])
        variant = ProductVariantFactory(product=product)
        ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=value,
        )
        duplicate_link = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=value,
        )
        with pytest.raises(ValidationError):
            duplicate_link.save()

    def test_unique_variant_attribute_constraint_raises_validation_error(self):
        attribute = AttributeFactory(name="Color")
        value1 = AttributeValueFactory(attribute=attribute, value="Red")
        value2 = AttributeValueFactory(attribute=attribute, value="Blue")
        product = ProductFactory(attributes=[attribute])
        variant = ProductVariantFactory(product=product)
        ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=value1,
        )
        duplicate_link = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=value2,
        )
        with pytest.raises(ValidationError):
            duplicate_link.save()


@pytest.mark.django_db
class TestProductImage:
    def test_str_method_returns_product_name_and_variant_sku_or_default(self):
        product = ProductFactory(name="Headphones")
        variant = ProductVariantFactory(product=product, sku="HEAD-001")
        image_with_variant = ProductImageFactory(product=product, variant=variant)
        image_without_variant = ProductImageFactory(product=product, variant=None)
        assert str(image_with_variant) == "Image for Headphones (SKU: HEAD-001)"
        assert str(image_without_variant) == "Image for Headphones"

    def test_save_method_sets_default_alt_text(self):
        product = ProductFactory(name="Speaker", slug="speaker")
        variant = ProductVariantFactory(product=product, sku="SPK-001")
        image_with_variant = ProductImageFactory(
            product=product,
            variant=variant,
            alt_text="",
        )
        image_without_variant = ProductImageFactory(
            product=product,
            variant=None,
            alt_text="",
        )
        assert image_with_variant.alt_text == "Image of speaker (SKU: SPK-001)"
        assert image_without_variant.alt_text == "Image of speaker"

    def test_save_method_preserves_existing_alt_text(self):
        product = ProductFactory(name="Monitor", slug="monitor")
        variant = ProductVariantFactory(product=product, sku="MON-001")
        custom_alt_text = "Custom alt text for monitor image"
        image = ProductImageFactory(
            product=product,
            variant=variant,
            alt_text=custom_alt_text,
        )
        assert image.alt_text == custom_alt_text

    def test_variant_must_belong_to_product(self):
        product1 = ProductFactory(name="Keyboard")
        product2 = ProductFactory(name="Mouse")
        variant = ProductVariantFactory(product=product2, sku="MOU-001")
        image_invalid = ProductImageFactory.build(
            product=product1,
            variant=variant,
        )
        with pytest.raises(ValidationError):
            image_invalid.save()
