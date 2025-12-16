import nested_admin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Attribute
from .models import AttributeValue
from .models import Category
from .models import Product
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
                    "is_active",
                ),
            },
        ),
    )
    list_display = ["name", "product_count", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["id", "created", "modified"]
    show_full_result_count = False
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_product_counts()

    @admin.display(description=_("Products"), ordering="product_count")
    def product_count(self, obj):
        return getattr(obj, "product_count", 0)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("General information"),
            {
                "fields": (
                    "attribute",
                    "value",
                    "sort_order",
                ),
            },
        ),
    )
    list_display = ["value", "attribute", "sort_order"]
    list_filter = [("attribute", admin.RelatedOnlyFieldListFilter)]
    search_fields = ["value", "attribute__name"]
    autocomplete_fields = ["attribute"]
    readonly_fields = ["id", "created", "modified"]
    show_full_result_count = False
    list_per_page = 10

    def has_module_permission(self, request):
        return False


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 0
    min_num = 1
    fields = ("value", "sort_order")
    ordering = ("sort_order", "value")


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
    list_display = ["name", "attribute_type"]
    list_filter = ["attribute_type"]
    search_fields = ["name"]
    readonly_fields = ["id", "created", "modified"]
    list_per_page = 10
    show_full_result_count = False


class ProductVariantAttributeValueInline(nested_admin.NestedTabularInline):
    model = ProductVariantAttributeValue
    extra = 0
    fields = ("attribute_value",)
    exclude = ("attribute",)
    autocomplete_fields = ["attribute_value"]


@admin.register(ProductVariant)
class ProductVariantAdmin(nested_admin.NestedModelAdmin):
    inlines = [ProductVariantAttributeValueInline]
    fieldsets = (
        (
            _("General information"),
            {
                "fields": (
                    "product",
                    "sku",
                    "price_override",
                    "stock_quantity",
                    "sort_order",
                    "is_active",
                ),
            },
        ),
    )
    list_display = ["product", "sku", "price_override", "stock_quantity", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["sku", "product__name"]
    autocomplete_fields = ["product"]
    readonly_fields = ["id", "created", "modified"]
    show_full_result_count = False
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_product()


class ProductVariantInline(nested_admin.NestedTabularInline):
    inlines = [ProductVariantAttributeValueInline]
    model = ProductVariant
    extra = 0
    min_num = 1
    fields = ("sku", "price_override", "stock_quantity", "sort_order", "is_active")
    ordering = ("sort_order", "sku")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_product()


class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 0
    fields = ("variant", "image", "alt_text", "sort_order", "is_active")
    ordering = ("sort_order",)
    autocomplete_fields = ["variant"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_product().with_variant()

    def get_formset(self, request, obj=None, **kwargs):
        self._parent_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "variant":
            qs = ProductVariant.objects.select_related("product")
            if getattr(self, "_parent_obj", None):
                qs = qs.filter(product=self._parent_obj)
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    inlines = [ProductVariantInline, ProductImageInline]
    fieldsets = (
        (
            _("General information"),
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "short_description",
                    "full_description",
                    "base_price",
                    "attributes",
                    "is_featured",
                    "is_active",
                ),
            },
        ),
    )
    list_display = ["name", "category", "base_price", "is_featured", "is_active"]
    list_filter = ["category", "is_featured", "is_active"]
    search_fields = ["name", "slug"]
    autocomplete_fields = ["category", "attributes"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["id", "created", "modified"]
    show_full_result_count = False
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_category().with_attributes()
