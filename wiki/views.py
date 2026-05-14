from django.shortcuts import render, get_object_or_404

from .models import Resource


def resource_detail(request, slug):
    resource = get_object_or_404(Resource, slug=slug, is_published=True)
    return render(request, 'wiki/resource_detail.html', {'resource': resource})


def resource_list(request):
    resources = (
        Resource.objects
        .filter(is_published=True)
        .exclude(category__slug='quickinfo')
        .select_related('category')
        .order_by('-created_at')
    )

    grouped = {}
    for resource in resources:
        key = resource.category.name if resource.category else None
        grouped.setdefault(key, []).append(resource)

    groups = [(label, items) for label, items in sorted(grouped.items(), key=lambda x: (x[0] is None, x[0]))]

    return render(request, 'wiki/resource_list.html', {'groups': groups})
