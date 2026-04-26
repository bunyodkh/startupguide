from django.shortcuts import render

from .models import EcosystemEntity, EntityCategory

def index(request):
    categories = EntityCategory.objects.prefetch_related('entities').all()

    

    return render(request, 'index.html', {'categories': categories})

