from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import TechnicalAnnouncement, CallToActionAnnouncement


@admin.register(TechnicalAnnouncement)
class TechnicalAnnouncementAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('title', 'message')
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'message')
        }),
        (_('Settings'), {
            'fields': ('is_active',)
        }),
    )


@admin.register(CallToActionAnnouncement)
class CallToActionAnnouncementAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('__str__', 'link_text', 'link', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('message', 'link_text')
    fieldsets = (
        (_('Content'), {
            'fields': ('message',)
        }),
        (_('Call to Action'), {
            'fields': ('link_text', 'link')
        }),
        (_('Settings'), {
            'fields': ('is_active',)
        }),
    )
