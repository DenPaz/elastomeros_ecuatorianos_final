from .models import Category


def categories_processor(request):
    categories = Category.objects.active().only("name", "slug").order_by("name")
    return {"product_categories": categories}
