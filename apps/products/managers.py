from django.apps import apps
from django.db import models
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.db.models import Prefetch
from django.db.models import Q


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class BaseManager(models.Manager.from_queryset(BaseQuerySet)):
    pass


class CategoryQuerySet(BaseQuerySet):
    pass


class CategoryManager(models.Manager.from_queryset(CategoryQuerySet)):
    pass


class AttributeQuerySet(BaseQuerySet):
    pass


class AttributeManager(models.Manager.from_queryset(AttributeQuerySet)):
    pass


class AttributeValueQuerySet(BaseQuerySet):
    pass


class AttributeValueManager(models.Manager.from_queryset(AttributeValueQuerySet)):
    pass


class ProductQuerySet(BaseQuerySet):
    pass


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    pass


class ProductAttributeQuerySet(models.QuerySet):
    pass


class ProductAttributeManager(
    models.Manager.from_queryset(ProductAttributeQuerySet),
):
    pass


class ProductVariantQuerySet(BaseQuerySet):
    pass


class ProductVariantManager(models.Manager.from_queryset(ProductVariantQuerySet)):
    pass


class ProductVariantAttributeValueQuerySet(models.QuerySet):
    pass


class ProductVariantAttributeValueManager(
    models.Manager.from_queryset(ProductVariantAttributeValueQuerySet),
):
    pass


class ProductImageQuerySet(BaseQuerySet):
    pass


class ProductImageManager(models.Manager.from_queryset(ProductImageQuerySet)):
    pass
