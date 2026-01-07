from django.apps import apps
from django.db import models
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Sum


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class CategoryQuerySet(ActiveQuerySet):
    def with_products(self):
        Product = apps.get_model("products", "Product")
        queryset = Product.objects.order_by("name")
        return self.prefetch_related(Prefetch("products", queryset=queryset))

    def with_active_products(self):
        Product = apps.get_model("products", "Product")
        queryset = Product.objects.active().order_by("name")
        return self.prefetch_related(
            Prefetch(
                "products",
                queryset=queryset,
                to_attr="active_products",
            ),
        )

    def with_product_counts(self):
        return self.annotate(
            product_count=Count(
                "products",
                distinct=True,
            ),
            active_product_count=Count(
                "products",
                filter=Q(products__is_active=True),
                distinct=True,
            ),
        )


class CategoryManager(models.Manager.from_queryset(CategoryQuerySet)):
    pass


class AttributeQuerySet(models.QuerySet):
    def with_values(self):
        AttributeValue = apps.get_model("products", "AttributeValue")
        queryset = AttributeValue.objects.order_by("sort_order", "value")
        return self.prefetch_related(Prefetch("values", queryset=queryset))


class AttributeManager(models.Manager.from_queryset(AttributeQuerySet)):
    pass


class AttributeValueQuerySet(models.QuerySet):
    def with_attribute(self):
        return self.select_related("attribute")


class AttributeValueManager(models.Manager.from_queryset(AttributeValueQuerySet)):
    def get_queryset(self):
        return super().get_queryset().with_attribute()


class ProductQuerySet(ActiveQuerySet):
    def with_category(self):
        return self.select_related("category")

    def with_attributes(self):
        Attribute = apps.get_model("products", "Attribute")
        queryset = Attribute.objects.order_by("name")
        return self.prefetch_related(Prefetch("attributes", queryset=queryset))

    def with_variants(self):
        ProductVariant = apps.get_model("products", "ProductVariant")
        queryset = ProductVariant.objects.order_by("sort_order", "sku")
        return self.prefetch_related(Prefetch("variants", queryset=queryset))

    def with_active_variants(self):
        ProductVariant = apps.get_model("products", "ProductVariant")
        queryset = ProductVariant.objects.active().order_by("sort_order", "sku")
        return self.prefetch_related(
            Prefetch(
                "variants",
                queryset=queryset,
                to_attr="active_variants",
            ),
        )

    def with_variants_summary(self):
        return self.annotate(
            min_price=Min(
                "variants__price",
                filter=Q(variants__is_active=True),
            ),
            max_price=Max(
                "variants__price",
                filter=Q(variants__is_active=True),
            ),
            total_stock=Sum(
                "variants__stock_quantity",
                filter=Q(variants__is_active=True),
            ),
        )


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    pass


class ProductVariantQuerySet(ActiveQuerySet):
    def with_product(self):
        return self.select_related("product")


class ProductVariantManager(models.Manager.from_queryset(ProductVariantQuerySet)):
    pass


class ProductVariantAttributeValueQuerySet(models.QuerySet):
    def with_product_variant(self):
        return self.select_related("product_variant")

    def with_attribute_value(self):
        return self.select_related("attribute_value__attribute")


class ProductVariantAttributeValueManager(
    models.Manager.from_queryset(ProductVariantAttributeValueQuerySet),
):
    def get_queryset(self):
        return super().get_queryset().with_product_variant().with_attribute_value()


class ProductImageQuerySet(ActiveQuerySet):
    def with_product(self):
        return self.select_related("product")

    def with_variant(self):
        return self.select_related("variant__product")


class ProductImageManager(models.Manager.from_queryset(ProductImageQuerySet)):
    pass
