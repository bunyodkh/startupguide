from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/create/', views.create_profile, name='create_profile'),
]
