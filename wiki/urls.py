from django.urls import path

from .views import resource_list

app_name = 'wiki'

urlpatterns = [
    path('resources/', resource_list, name='resource_list'),
]
