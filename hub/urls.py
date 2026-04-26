from django.urls import path

app_name = 'hub'

from .views import index

urlpatterns = [
    path('', index, name='index'),
]