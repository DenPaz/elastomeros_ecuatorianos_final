from django.apps import apps
from django.db import models
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
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
    def get_queryset(self):
        return super().get_queryset().with_category()


class ProductAttributeQuerySet(models.QuerySet):
    pass


class ProductAttributeManager(models.Manager.from_queryset(ProductAttributeQuerySet)):
    pass


class ProductVariantQuerySet(ActiveQuerySet):
    pass


class ProductVariantManager(models.Manager.from_queryset(ProductVariantQuerySet)):
    pass


class ProductVariantAttributeValueQuerySet(models.QuerySet):
    pass


class ProductVariantAttributeValueManager(
    models.Manager.from_queryset(ProductVariantAttributeValueQuerySet),
):
    pass


class ProductImageQuerySet(ActiveQuerySet):
    pass


class ProductImageManager(models.Manager.from_queryset(ProductImageQuerySet)):
    pass
