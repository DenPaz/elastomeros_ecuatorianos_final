from django.db import models
from django.utils.translation import gettext_lazy as _


class AttributeType(models.TextChoices):
    CAPACITY = "CAPACITY", _("Capacity")
    COLOR = "COLOR", _("Color")
    DEPTH = "DEPTH", _("Depth")
    HEIGHT = "HEIGHT", _("Height")
    LENGTH = "LENGTH", _("Length")
    MATERIAL = "MATERIAL", _("Material")
    QUANTITY = "QUANTITY", _("Quantity")
    SIZE = "SIZE", _("Size")
    VOLUME = "VOLUME", _("Volume")
    WEIGHT = "WEIGHT", _("Weight")
    WIDTH = "WIDTH", _("Width")
    OTHER = "OTHER", _("Other")
