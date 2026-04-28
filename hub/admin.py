from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import EntityCategory, EcosystemEntity, Region


@admin.register(Region)
class RegionAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(EntityCategory)
class EntityCategoryAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(EcosystemEntity)
class EcosystemEntityAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('get_logo', 'name', 'category', 'city', 'status', 'start_date', 'end_date', 'registration_deadline', 'is_active')
    list_display_links = ('get_logo', 'name')
    list_filter = ('category', 'status', 'is_active', 'has_physical_space', 'regions')
    search_fields = ('name', 'short_name', 'category__name')
    autocomplete_fields = ['parent', 'category', 'organizers']
    filter_horizontal = ('coordinators', 'regions')

    fieldsets = (
        (_("General"), {
            'fields': ('name', 'short_name', 'category', 'parent', 'description', 'website', 'is_active'),
        }),
        (_("Media"), {
            'fields': ('logo', 'cover_image'),
        }),
        (_("Location"), {
            'fields': ('has_physical_space', 'city', 'regions'),
        }),
        (_("Program Details"), {
            'fields': ('status', 'start_date', 'end_date', 'registration_deadline'),
        }),
        (_("People"), {
            'fields': ('organizers', 'coordinators'),
        }),
        (_("Other"), {
            'fields': ('founded_year',),
        }),
    )

    def get_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height: 32px; border-radius: 4px; object-fit: contain;" />', obj.logo.url)
        return format_html('<span class="text-gray-400 text-xs">{}</span>', _("No logo"))
    get_logo.short_description = _("Logo")