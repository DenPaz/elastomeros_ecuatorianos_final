from django.db import models
from django.utils.translation import gettext_lazy as _


class CartStatus(models.TextChoices):
    OPEN = "OPEN", _("Open")
    CHECKED_OUT = "CHECKED_OUT", _("Checked out")
    ABANDONED = "ABANDONED", _("Abandoned")
