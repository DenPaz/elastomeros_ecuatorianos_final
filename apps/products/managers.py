from django.apps import apps
from django.db import models
from django.db.models import Count
from django.db.models import Prefetch
from django.db.models import Q


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class CategoryQuerySet(ActiveQuerySet):
    def with_products(self):
        Product = apps.get_model("products", "Product")
        queryset = Product.objects.active().order_by("name")
        return self.prefetch_related(Prefetch("products", queryset=queryset))

    def with_product_counts(self):
        return self.annotate(
            product_count=Count(
                "products",
                filter=Q(products__is_active=True),
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
        queryset = Attribute.objects.with_values().order_by("name")
        return self.prefetch_related(Prefetch("attributes", queryset=queryset))


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    pass


class ProductAttributeQuerySet(models.QuerySet):
    def with_product(self):
        return self.select_related("product")

    def with_attribute(self):
        return self.select_related("attribute")


class ProductAttributeManager(models.Manager.from_queryset(ProductAttributeQuerySet)):
    def get_queryset(self):
        return super().get_queryset().with_product().with_attribute()


class ProductVariantQuerySet(ActiveQuerySet):
    def with_product(self):
        return self.select_related("product")


class ProductVariantManager(models.Manager.from_queryset(ProductVariantQuerySet)):
    def get_queryset(self):
        return super().get_queryset().with_product()


class ProductVariantAttributeValueQuerySet(models.QuerySet):
    def with_product_variant(self):
        return self.select_related("product_variant")

    def with_attribute(self):
        return self.select_related("attribute_value__attribute")


class ProductVariantAttributeValueManager(
    models.Manager.from_queryset(ProductVariantAttributeValueQuerySet),
):
    def get_queryset(self):
        return super().get_queryset().with_product_variant().with_attribute()


class ProductImageQuerySet(ActiveQuerySet):
    pass


class ProductImageManager(models.Manager.from_queryset(ProductImageQuerySet)):
    pass
