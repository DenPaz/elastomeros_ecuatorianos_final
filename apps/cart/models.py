from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel

from .choices import CartStatus
from .managers import CartItemManager
from .managers import CartManager


class Cart(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        related_name="carts",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session_key = models.CharField(
        verbose_name=_("Session key"),
        max_length=40,
        blank=True,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=CartStatus.choices,
        default=CartStatus.OPEN,
    )

    objects = CartManager()

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        indexes = [
            models.Index(fields=["session_key"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["session_key", "status"]),
            models.Index(fields=["-modified"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=(
                    Q(status=CartStatus.OPEN)
                    & Q(user__isnull=False)
                    & Q(session_key="")
                ),
                name="unique_open_cart_per_user",
            ),
            models.UniqueConstraint(
                fields=["session_key"],
                condition=(
                    Q(status=CartStatus.OPEN)
                    & Q(user__isnull=True)
                    & ~Q(session_key="")
                ),
                name="unique_open_cart_per_session",
            ),
            models.CheckConstraint(
                condition=Q(user__isnull=False) | ~Q(session_key=""),
                name="cart_requires_user_or_session_key",
            ),
        ]
        ordering = ["-modified"]

    def __str__(self):
        if self.user_id:
            return f"Cart of {self.user.email} ({self.status})"
        return f"Cart with session {self.session_key} ({self.status})"


class CartItem(UUIDModel, TimeStampedModel):
    cart = models.ForeignKey(
        to=Cart,
        verbose_name=_("Cart"),
        related_name="items",
        on_delete=models.CASCADE,
    )
    variant = models.ForeignKey(
        to="products.ProductVariant",
        verbose_name=_("Product variant"),
        related_name="cart_items",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
        validators=[MinValueValidator(1)],
        default=1,
    )

    objects = CartItemManager()

    class Meta:
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"],
                name="unique_variant_per_cart",
            ),
        ]
        ordering = ["created"]

    def __str__(self):
        return f"{self.cart_id} - {self.variant.sku} x {self.quantity}"

    @property
    def line_total(self):
        return self.variant.price * self.quantity
