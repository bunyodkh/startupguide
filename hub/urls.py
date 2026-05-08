from django.urls import path

from .views import (
    index,
    program_detail,
    program_apply,
    cycle_register_page,
    program_manage,
    form_responses,
    cycle_list_page,
    cycle_create_page,
    cycle_edit_page,
    cycle_archive_view,
    cycle_manage_htmx,
    cycle_htmx_item,
    cycle_htmx_edit,
    cycle_htmx_create,
    cycle_toggle_htmx,
    form_settings_htmx,
    field_add_htmx,
    field_delete_htmx,
)

app_name = 'hub'

urlpatterns = [
    path('', index, name='index'),
    path('r/<slug:slug>/', cycle_register_page, name='cycle_register'),
    path('programs/<slug:slug>/', program_detail, name='view_program'),
    path('programs/<slug:slug>/apply/', program_apply, name='program_apply'),
    path('programs/<int:pk>/manage/', program_manage, name='program_manage'),
    path('programs/<int:pk>/responses/', form_responses, name='form_responses'),
    # Full-page cycle management
    path('programs/<int:pk>/cycles/', cycle_list_page, name='cycle_list'),
    path('programs/<int:pk>/cycles/new/', cycle_create_page, name='cycle_create_page'),
    path('programs/<int:pk>/cycles/<int:cycle_pk>/edit-page/', cycle_edit_page, name='cycle_edit_page'),
    path('programs/<int:pk>/cycles/<int:cycle_pk>/archive/', cycle_archive_view, name='cycle_archive'),
    # HTMX — cycles
    path('programs/<int:pk>/cycles/<int:cycle_pk>/', cycle_htmx_item, name='cycle_item'),
    path('programs/<int:pk>/cycles/<int:cycle_pk>/edit/', cycle_htmx_edit, name='cycle_edit'),
    path('programs/<int:pk>/cycles/add/', cycle_htmx_create, name='cycle_create'),
    path('programs/<int:pk>/cycles/<int:cycle_pk>/toggle/', cycle_toggle_htmx, name='cycle_toggle'),
    # HTMX — active cycle inline edit
    path('programs/<int:pk>/cycles/active/save/', cycle_manage_htmx, name='cycle_manage'),
    # HTMX — form settings
    path('programs/<int:pk>/cycles/<int:cycle_pk>/form/settings/', form_settings_htmx, name='form_settings'),
    path('programs/<int:pk>/cycles/<int:cycle_pk>/form/fields/add/', field_add_htmx, name='field_add'),
    path('programs/<int:pk>/cycles/<int:cycle_pk>/form/fields/<int:field_pk>/delete/', field_delete_htmx, name='field_delete'),
]
