from django.apps import apps
from django.db import models
from django.db.models import Prefetch


class CartQuerySet(models.QuerySet):
    def open(self):
        return self.filter(status="OPEN")

    def with_items(self):
        CartItem = apps.get_model("cart", "CartItem")
        queryset = CartItem.objects.select_related("variant__product")
        return self.prefetch_related(Prefetch("items", queryset=queryset))


class CartManager(models.Manager.from_queryset(CartQuerySet)):
    pass


class CartItemQuerySet(models.QuerySet):
    def with_cart_and_variant(self):
        return self.select_related("cart", "variant__product")


class CartItemManager(models.Manager.from_queryset(CartItemQuerySet)):
    def get_queryset(self):
        return super().get_queryset().with_cart_and_variant()
