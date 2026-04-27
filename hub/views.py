from django.shortcuts import render

from users.models import BuilderProfile
from wiki.models import Resource
from .models import EcosystemEntity, EntityCategory


def index(request):
    categories = EntityCategory.objects.prefetch_related('entities').all()

    people = (
        BuilderProfile.objects
        .filter(is_published=True, show_on_main_page=True)
        .select_related('user')
        .prefetch_related('affiliated_entities')
        .order_by('user__first_name', 'user__last_name')
    )

    places = (
        EcosystemEntity.objects
        .filter(has_physical_space=True, is_active=True)
        .select_related('category', 'parent')
        .order_by('name')
    )

    programs = (
        EcosystemEntity.objects
        .filter(has_physical_space=False, is_active=True)
        .select_related('category', 'parent')
        .order_by('name')
    )

    resources = (
        Resource.objects
        .filter(is_published=True)
        .select_related('category', 'author')
        .order_by('category__name', 'title')
    )

    return render(request, 'index.html', {
        'categories': categories,
        'people': people,
        'places': places,
        'programs': programs,
        'resources': resources,
    })

