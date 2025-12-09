from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel

from apps.core.utils import get_default_image_url
from apps.core.validators import FileSizeValidator

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
        unique=True,
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
    image = models.ImageField(
        verbose_name=_("Image"),
        upload_to="products/categories/",
        validators=[
            FileSizeValidator(max_size=5, unit="MB"),
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
        ],
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        db_index=True,
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    # TODO: Implement when views are ready
    def get_absolute_url(self): ...

    def get_image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return get_default_image_url()


class Attribute(TimeStampedModel):
    name = models.CharField(
        verbose_name=_("Name"),
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
        db_index=True,
    )

    objects = AttributeManager()

    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
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
    sort_order = models.PositiveIntegerField(
        verbose_name=_("Sort order"),
        default=0,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        db_index=True,
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
        db_index=True,
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
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        db_index=True,
    )

    objects = ProductManager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        constraints = [
            models.UniqueConstraint(
                "category",
                Lower("name"),
                name="unique_product_name_per_category",
            ),
        ]
        indexes = [
            models.Index(fields=["-created"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    # TODO: Implement when views are ready
    def get_absolute_url(self): ...


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        to=Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(
        to=Attribute,
        verbose_name=_("Attribute"),
        on_delete=models.CASCADE,
    )

    objects = ProductAttributeManager()

    class Meta:
        verbose_name = _("Product-Attribute relation")
        verbose_name_plural = _("Product-Attribute relations")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute"],
                name="unique_product_attribute_relation",
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
    sort_order = models.PositiveIntegerField(
        verbose_name=_("Sort order"),
        default=0,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        db_index=True,
    )

    objects = ProductVariantManager()

    class Meta:
        verbose_name = _("Product variant")
        verbose_name_plural = _("Product variants")
        ordering = ["product", "sort_order", "sku"]

    def __str__(self):
        return f"{self.product.name} ({self.sku})"

    @property
    def price(self):
        if self.price_override is not None:
            return self.price_override
        return self.product.base_price


class ProductVariantAttributeValue(models.Model):
    product_variant = models.ForeignKey(
        to=ProductVariant,
        verbose_name=_("Product variant"),
        on_delete=models.CASCADE,
    )
    attribute_value = models.ForeignKey(
        to=AttributeValue,
        verbose_name=_("Attribute value"),
        on_delete=models.CASCADE,
    )

    objects = ProductVariantAttributeValueManager()

    class Meta:
        verbose_name = _("Product variant-Attribute value relation")
        verbose_name_plural = _("Product variant-Attribute value relations")
        constraints = [
            models.UniqueConstraint(
                fields=["product_variant", "attribute_value"],
                name="unique_product_variant_attribute_value_relation",
            ),
        ]
        ordering = ["product_variant", "attribute_value"]

    def __str__(self):
        return f"{self.product_variant.sku} - {self.attribute_value}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.product_variant or not self.attribute_value:
            return

        attribute = self.attribute_value.attribute

        qs = ProductVariantAttributeValue.objects.filter(
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
                        params={"attribute": attribute.name},
                    ),
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
    sort_order = models.PositiveIntegerField(
        verbose_name=_("Sort order"),
        default=0,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        db_index=True,
    )

    objects = ProductImageManager()

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")
        ordering = ["product", "sort_order"]

    def __str__(self):
        if self.variant:
            return f"Image #{self.id} for {self.product.name} ({self.variant.sku})"
        return f"Image #{self.id} for {self.product.name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.alt_text:
            if self.variant:
                self.alt_text = f"{self.product.slug} ({self.variant.sku})"
            else:
                self.alt_text = f"{self.product.slug}"
        super().save(*args, **kwargs)

    def clean(self):
        if self.variant and self.variant.product != self.product:
            raise ValidationError(
                {
                    "variant": _(
                        (
                            "The selected variant does not belong to the specified "
                            "product."
                        ),
                    ),
                },
            )
