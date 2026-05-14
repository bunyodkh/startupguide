from django.urls import path

from .views import resource_list, resource_detail

app_name = 'wiki'

urlpatterns = [
    path('resources/', resource_list, name='resource_list'),
    path('resources/<slug:slug>/', resource_detail, name='resource_detail'),
]
