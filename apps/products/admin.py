from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Attribute
from .models import AttributeValue
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("General information"),
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "is_active",
                ),
            },
        ),
    )
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["id", "created", "modified"]
    list_per_page = 10


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 0
    min_num = 1


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    inlines = [AttributeValueInline]
    fieldsets = (
        (
            _("General information"),
            {
                "fields": (
                    "name",
                    "attribute_type",
                    "description",
                ),
            },
        ),
    )
    list_display = [
        "name",
        "attribute_type",
    ]
    list_filter = ["attribute_type"]
    search_fields = ["name"]
    readonly_fields = ["id", "created", "modified"]
    list_per_page = 10
