from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from django.utils.translation import gettext_lazy as _
from .models import ResourceCategory, Resource

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Resource)
class ResourceAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author__first_name')
    
    # Автоматическое создание slug из заголовка
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (_('Main Info'), {
            'fields': ('title', 'slug', 'category', 'author', 'is_published')
        }),
        (_('Content & Description'), {
            'fields': ('content',)
        }),
        (_('Media & Attachments'), {
            'fields': ('logo', 'attached_file', 'video_url')
        }),
    )