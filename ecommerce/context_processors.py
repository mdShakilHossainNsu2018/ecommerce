from products.models import Category


def get_context(request):
    categories = Category.objects.all()
    context = {
        "categories": categories,
    }

    return context
