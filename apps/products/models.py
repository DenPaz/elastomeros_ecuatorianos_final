from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel

from apps.core.fields import OrderField
from apps.core.validators import FileSizeValidator

from .choices import AttributeType
from .managers import AttributeManager
from .managers import AttributeValueManager
from .managers import CategoryManager
from .managers import ProductAttributeManager
from .managers import ProductImageManager
from .managers import ProductManager
from .managers import ProductVariantAttributeValueManager
from .managers import ProductVariantManager
from .utils import product_image_upload_to


class Category(UUIDModel, TimeStampedModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=255,
        unique=True,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_category_name_case_insensitive",
            ),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Attribute(TimeStampedModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    attribute_type = models.CharField(
        verbose_name=_("Attribute type"),
        max_length=50,
        choices=AttributeType.choices,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )

    objects = AttributeManager()

    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["attribute_type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_attribute_name_case_insensitive",
            ),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class AttributeValue(TimeStampedModel):
    attribute = models.ForeignKey(
        to=Attribute,
        verbose_name=_("Attribute"),
        related_name="values",
        on_delete=models.CASCADE,
    )
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=255,
    )
    sort_order = OrderField(
        verbose_name=_("Sort order"),
        for_fields=["attribute"],
        blank=True,
        null=True,
    )

    objects = AttributeValueManager()

    class Meta:
        verbose_name = _("Attribute value")
        verbose_name_plural = _("Attribute values")
        constraints = [
            models.UniqueConstraint(
                "attribute",
                Lower("value"),
                name="unique_attribute_value_per_attribute",
            ),
        ]
        ordering = ["attribute", "sort_order", "value"]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(UUIDModel, TimeStampedModel):
    category = models.ForeignKey(
        to=Category,
        verbose_name=_("Category"),
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=255,
        unique=True,
    )
    short_description = models.TextField(
        verbose_name=_("Short description"),
        blank=True,
    )
    full_description = models.TextField(
        verbose_name=_("Full description"),
        blank=True,
    )
    base_price = models.DecimalField(
        verbose_name=_("Base price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    attributes = models.ManyToManyField(
        to=Attribute,
        through="ProductAttribute",
        verbose_name=_("Attributes"),
        related_name="products",
        blank=True,
    )
    is_featured = models.BooleanField(
        verbose_name=_("Featured"),
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
    )

    objects = ProductManager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["-created"]),
        ]
        constraints = [
            models.UniqueConstraint(
                "category",
                Lower("name"),
                name="unique_product_name_per_category_case_insensitive",
            ),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        to=Product,
        verbose_name=_("Product"),
        related_name="product_attributes",
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(
        to=Attribute,
        verbose_name=_("Attribute"),
        related_name="product_attributes",
        on_delete=models.PROTECT,
    )

    objects = ProductAttributeManager()

    class Meta:
        verbose_name = _("Product-attribute link")
        verbose_name_plural = _("Product-attribute links")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute"],
                name="unique_product_attribute_link",
            ),
        ]
        ordering = ["product", "attribute"]

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}"


class ProductVariant(UUIDModel, TimeStampedModel):
    product = models.ForeignKey(
        to=Product,
        verbose_name=_("Product"),
        related_name="variants",
        on_delete=models.CASCADE,
    )
    sku = models.CharField(
        verbose_name=_("SKU"),
        max_length=100,
        unique=True,
    )
    price_override = models.DecimalField(
        verbose_name=_("Price override"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        blank=True,
        null=True,
    )
    stock_quantity = models.PositiveIntegerField(
        verbose_name=_("Stock quantity"),
        default=0,
    )
    attribute_values = models.ManyToManyField(
        to=AttributeValue,
        through="ProductVariantAttributeValue",
        verbose_name=_("Attribute values"),
        related_name="product_variants",
        blank=True,
    )
    sort_order = OrderField(
        verbose_name=_("Sort order"),
        for_fields=["product"],
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
    )

    objects = ProductVariantManager()

    class Meta:
        verbose_name = _("Product variant")
        verbose_name_plural = _("Product variants")
        indexes = [
            models.Index(fields=["is_active"]),
        ]
        ordering = ["product", "sort_order", "sku"]

    def __str__(self):
        return f"{self.product.name} (SKU: {self.sku})"

    @property
    def price(self):
        return (
            self.price_override
            if self.price_override is not None
            else self.product.base_price
        )


class ProductVariantAttributeValue(models.Model):
    product_variant = models.ForeignKey(
        to=ProductVariant,
        verbose_name=_("Product variant"),
        related_name="variant_attribute_values",
        on_delete=models.CASCADE,
    )
    attribute_value = models.ForeignKey(
        to=AttributeValue,
        verbose_name=_("Attribute value"),
        related_name="variant_attribute_values",
        on_delete=models.PROTECT,
    )

    objects = ProductVariantAttributeValueManager()

    class Meta:
        verbose_name = _("Product-variant-attribute-value link")
        verbose_name_plural = _("Product-variant-attribute-value links")
        constraints = [
            # No duplicate attribute values for the same product variant
            models.UniqueConstraint(
                fields=["product_variant", "attribute_value"],
                name="unique_product_variant_attribute_value_link",
            ),
        ]
        ordering = ["product_variant", "attribute_value"]

    def __str__(self):
        return f"{self.product_variant.sku} - {self.attribute_value}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.product_variant or not self.attribute_value:
            return

        product_variant = self.product_variant
        product = product_variant.product
        attribute = self.attribute_value.attribute

        # One value per attribute per product variant
        qs = self.__class__.objects.filter(
            product_variant=self.product_variant,
            attribute_value__attribute=attribute,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                {
                    "attribute_value": _(
                        (
                            "This product variant already has a value for the "
                            "attribute '%(attribute)s'."
                        ),
                    )
                    % {"attribute": attribute.name},
                },
            )

        # The attribute must be linked to the product
        if not product.attributes.filter(pk=attribute.pk).exists():
            raise ValidationError(
                {
                    "attribute_value": _(
                        (
                            "The attribute '%(attribute)s' is not associated "
                            "with the product '%(product)s'."
                        ),
                    )
                    % {"attribute": attribute.name, "product": product.name},
                },
            )

        # Unique variant combination per product
        self._validate_unique_variant_combination()

    def _validate_unique_variant_combination(self):
        product_variant = self.product_variant
        product = product_variant.product

        current_attribute_value_ids = set(
            self.__class__.objects.filter(product_variant=product_variant)
            .exclude(pk=self.pk)
            .values_list("attribute_value_id", flat=True),
        )
        current_attribute_value_ids.add(self.attribute_value_id)

        if not current_attribute_value_ids:
            return

        variant_qs = (
            ProductVariant.objects.filter(product=product)
            .exclude(pk=product_variant.pk)
            .annotate(num_values=models.Count("attribute_values", distinct=True))
            .filter(num_values=len(current_attribute_value_ids))
        )

        for other in variant_qs:
            other_value_ids = set(
                self.__class__.objects.filter(product_variant=other).values_list(
                    "attribute_value_id",
                    flat=True,
                ),
            )
            if current_attribute_value_ids == other_value_ids:
                raise ValidationError(
                    {
                        "attribute_value": _(
                            "This combination of attribute values already "
                            "exists for another variant of the product "
                            "'%(product)s'.",
                        )
                        % {"product": product.name},
                    },
                )


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        to=Product,
        verbose_name=_("Product"),
        related_name="images",
        on_delete=models.CASCADE,
    )
    variant = models.ForeignKey(
        to=ProductVariant,
        verbose_name=_("Product variant"),
        related_name="images",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name=_("Image"),
        upload_to=product_image_upload_to,
        validators=[
            FileSizeValidator(max_size=5, unit="MB"),
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
        ],
    )
    alt_text = models.CharField(
        verbose_name=_("Alt text"),
        max_length=255,
        blank=True,
    )
    sort_order = OrderField(
        verbose_name=_("Sort order"),
        for_fields=["product"],
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
    )

    objects = ProductImageManager()

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")
        indexes = [
            models.Index(fields=["is_active"]),
        ]
        ordering = ["product", "sort_order"]

    def __str__(self):
        if self.variant:
            return f"Image for {self.product.name} (SKU: {self.variant.sku})"
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.alt_text:
            if self.variant:
                self.alt_text = (
                    f"Image of {self.product.slug} (SKU: {self.variant.sku})"
                )
            else:
                self.alt_text = f"Image of {self.product.slug}"
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.variant and self.variant.product != self.product:
            raise ValidationError(
                {
                    "variant": _(
                        "The selected variant '%(variant)s' does not belong "
                        "to the product '%(product)s'.",
                    )
                    % {
                        "variant": self.variant.sku,
                        "product": self.product.name,
                    },
                },
            )
