from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('users/profile/', views.manage_profile, name='manage_profile'),
    path('people/<slug:slug>/', views.view_profile, name='view_profile'),
]
