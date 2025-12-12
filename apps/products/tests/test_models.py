from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from .factories import AttributeFactory
from .factories import AttributeValueFactory
from .factories import CategoryFactory
from .factories import ProductAttributeFactory
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


@pytest.mark.django_db
class TestAttribute:
    def test_str_method_returns_name(self):
        attribute = AttributeFactory(name="Color")
        assert str(attribute) == "Color"

    def test_name_is_unique_case_insensitive(self):
        AttributeFactory(name="Material")
        with pytest.raises(IntegrityError):
            AttributeFactory(name="material")

    def test_post_generation_values_creates_attribute_values(self):
        attribute = AttributeFactory(values=["Red", "Blue", "Green"])
        values = list(attribute.values.values_list("value", flat=True))
        assert set(values) == {"Red", "Blue", "Green"}


@pytest.mark.django_db
class TestAttributeValue:
    def test_str_method_returns_attribute_name_and_value(self):
        attribute = AttributeFactory(name="Size")
        attribute_value = AttributeValueFactory(attribute=attribute, value="Large")
        assert str(attribute_value) == "Size: Large"

    def test_unique_value_per_attribute_case_insensitive(self):
        attribute = AttributeFactory(name="Brand")
        AttributeValueFactory(attribute=attribute, value="Nike")
        with pytest.raises(IntegrityError):
            AttributeValueFactory(attribute=attribute, value="nike")

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
        category = CategoryFactory(name="Gadgets")
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

    def test_post_generation_attributes_creates_product_attributes(self):
        attribute1 = AttributeFactory(name="Warranty")
        attribute2 = AttributeFactory(name="Battery Life")
        product = ProductFactory(attributes=[attribute1, attribute2])
        linked_attributes = list(product.attributes.all())
        assert set(linked_attributes) == {attribute1, attribute2}


@pytest.mark.django_db
class TestProductAttribute:
    def test_str_method_returns_product_and_attribute_names(self):
        product = ProductFactory(name="Laptop")
        attribute = AttributeFactory(name="RAM")
        link = ProductAttributeFactory(product=product, attribute=attribute)
        assert str(link) == "Laptop - RAM"

    def test_unique_product_attribute_link(self):
        product = ProductFactory()
        attribute = AttributeFactory()
        ProductAttributeFactory(product=product, attribute=attribute)
        with pytest.raises(IntegrityError):
            ProductAttributeFactory(product=product, attribute=attribute)

    def test_same_attribute_allowed_for_different_products(self):
        attribute = AttributeFactory(name="Storage")
        product1 = ProductFactory(name="Phone")
        product2 = ProductFactory(name="Tablet")
        link1 = ProductAttributeFactory(product=product1, attribute=attribute)
        link2 = ProductAttributeFactory(product=product2, attribute=attribute)
        assert link1.pk != link2.pk
        assert attribute in product1.attributes.all()
        assert attribute in product2.attributes.all()
        assert product1 in attribute.products.all()
        assert product2 in attribute.products.all()


@pytest.mark.django_db
class TestProductVariant:
    def test_str_method_returns_product_name_and_variant_sku(self):
        product = ProductFactory(name="Camera")
        variant = ProductVariantFactory(product=product, sku="CAM-001")
        assert str(variant) == "Camera (SKU: CAM-001)"

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

    def test_post_generation_attribute_values_creates_variant_attribute_values(self):
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


@pytest.mark.django_db
class TestProductVariantAttributeValue:
    def test_str_method_returns_product_variant_sku_and_attribute_value(self):
        variant = ProductVariantFactory(sku="CAM-001")
        attribute = AttributeFactory(name="Color")
        attribute_value = AttributeValueFactory(attribute=attribute, value="Black")
        pvav = ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=attribute_value,
        )
        assert str(pvav) == "CAM-001 - Color: Black"

    def test_unique_product_variant_attribute_value_link(self):
        variant = ProductVariantFactory()
        attribute = AttributeFactory(name="Color")
        attribute_value = AttributeValueFactory(attribute=attribute, value="Red")
        ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=attribute_value,
        )
        pvav_duplicate = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=attribute_value,
        )
        with pytest.raises(ValidationError):
            pvav_duplicate.save()

    def test_one_value_per_attribute_per_variant(self):
        product = ProductFactory()
        attribute = AttributeFactory(name="Size")
        value1 = AttributeValueFactory(attribute=attribute, value="Small")
        value2 = AttributeValueFactory(attribute=attribute, value="Large")
        variant = ProductVariantFactory(product=product)
        ProductVariantAttributeValueFactory(
            product_variant=variant,
            attribute_value=value1,
        )
        pvav_conflict = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=value2,
        )
        with pytest.raises(ValidationError):
            pvav_conflict.save()

    def test_attribute_must_be_linked_to_product(self):
        product = ProductFactory()
        variant = ProductVariantFactory(product=product)
        attribute = AttributeFactory(name="Material")
        attribute_value = AttributeValueFactory(attribute=attribute, value="Cotton")
        pvav_invalid = ProductVariantAttributeValueFactory.build(
            product_variant=variant,
            attribute_value=attribute_value,
        )
        with pytest.raises(ValidationError):
            pvav_invalid.save()

    def test_unique_combination_of_attribute_value_per_product(self):
        attribute1 = AttributeFactory(name="Color")
        value1 = AttributeValueFactory(attribute=attribute1, value="Red")
        attribute2 = AttributeFactory(name="Size")
        value2 = AttributeValueFactory(attribute=attribute2, value="Medium")
        product = ProductFactory()
        variant1 = ProductVariantFactory(product=product)
        ProductVariantAttributeValueFactory(
            product_variant=variant1,
            attribute_value=value1,
        )
        ProductVariantAttributeValueFactory(
            product_variant=variant1,
            attribute_value=value2,
        )
        assert set(variant1.attribute_values.all()) == {value1, value2}
        variant2 = ProductVariantFactory(product=product)
        ProductVariantAttributeValueFactory(
            product_variant=variant2,
            attribute_value=value1,
        )
        assert set(variant2.attribute_values.all()) == {value1}
        pvav_duplicate = ProductVariantAttributeValueFactory.build(
            product_variant=variant2,
            attribute_value=value1,
        )
        with pytest.raises(ValidationError):
            pvav_duplicate.save()

    def test_same_attribute_value_allowed_for_different_variants(self):
        attribute1 = AttributeFactory(name="Color")
        value1 = AttributeValueFactory(attribute=attribute1, value="Blue")
        attribute2 = AttributeFactory(name="Size")
        value2 = AttributeValueFactory(attribute=attribute2, value="Large")
        product1 = ProductFactory()
        product2 = ProductFactory()
        variant1 = ProductVariantFactory(product=product1)
        variant2 = ProductVariantFactory(product=product2)
        ProductVariantAttributeValueFactory(
            product_variant=variant1,
            attribute_value=value1,
        )
        ProductVariantAttributeValueFactory(
            product_variant=variant1,
            attribute_value=value2,
        )
        ProductVariantAttributeValueFactory(
            product_variant=variant2,
            attribute_value=value1,
        )
        ProductVariantAttributeValueFactory(
            product_variant=variant2,
            attribute_value=value2,
        )
        assert set(variant1.attribute_values.all()) == {value1, value2}
        assert set(variant2.attribute_values.all()) == {value1, value2}
        assert variant1.product != variant2.product


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
