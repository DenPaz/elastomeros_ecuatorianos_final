import nested_admin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Attribute
from .models import AttributeValue
from .models import Category
from .models import Product
from .models import ProductAttribute
from .models import ProductImage
from .models import ProductVariant
from .models import ProductVariantAttributeValue


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
                    "image",
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


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    search_fields = ["attribute__name", "value"]
    autocomplete_fields = ["attribute"]

    def has_module_permission(self, request):
        return False


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
                    "description",
                    "is_active",
                ),
            },
        ),
    )
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    readonly_fields = ["id", "created", "modified"]
    list_per_page = 10
