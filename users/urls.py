from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.manage_profile, name='manage_profile'),
]
