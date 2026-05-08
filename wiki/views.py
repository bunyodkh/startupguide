from django.shortcuts import render

from .models import Resource


def resource_list(request):
    resources = (
        Resource.objects
        .filter(is_published=True)
        .select_related('category')
        .order_by('-created_at')
    )

    grouped = {}
    for resource in resources:
        key = resource.category.name if resource.category else None
        grouped.setdefault(key, []).append(resource)

    groups = [(label, items) for label, items in sorted(grouped.items(), key=lambda x: (x[0] is None, x[0]))]

    return render(request, 'wiki/resource_list.html', {'groups': groups})
