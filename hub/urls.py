from django.urls import path

app_name = 'hub'

from .views import index, program_detail

urlpatterns = [
    path('', index, name='index'),
    path('programs/<int:pk>/', program_detail, name='view_program'),
]