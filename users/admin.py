from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from modeltranslation.admin import TabbedTranslationAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import BuilderProfile

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)


@admin.register(Site)
class CustomSiteAdmin(ModelAdmin, SiteAdmin):
    pass


@admin.register(User)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets


@admin.register(Group)
class CustomGroupAdmin(ModelAdmin, GroupAdmin):
    pass

@admin.register(BuilderProfile)
class BuilderProfileAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('get_avatar', 'user', 'position', 'is_expert', 'is_published', 'show_on_main_page', 'created_at')
    list_display_links = ('get_avatar', 'user')
    list_filter = ('is_published', 'show_on_main_page', 'is_expert', 'gender')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'position', 'expertise')
    readonly_fields = ('created_at', 'updated_at', 'get_avatar_preview')
    autocomplete_fields = ['affiliated_entities']

    fieldsets = (
        (_('Account Status'), {
            'fields': ('user', 'is_published', 'show_on_main_page')
        }),
        (_('Media'), {
            'fields': ('photo', 'get_avatar_preview')
        }),
        (_('Professional Information'), {
            'fields': ('position', 'bio', 'affiliated_entities')
        }),
        (_('Expert'), {
            'fields': ('is_expert', 'expertise')
        }),
        (_('Contacts'), {
            'fields': ('linkedin_url', 'telegram_handle')
        }),
        (_('Personal'), {
            'fields': ('gender',)
        }),
        (_('System Info'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_avatar(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />', obj.photo.url)
        return format_html('<span class="text-gray-400 text-xs">{}</span>', _("No photo"))
    get_avatar.short_description = _('Photo')

    def get_avatar_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 150px; border-radius: 8px;" />', obj.photo.url)
        return _("No photo uploaded yet.")
    get_avatar_preview.short_description = _('Photo Preview')