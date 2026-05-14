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
    list_display = ('title', 'category', 'author', 'is_published', 'show_on_quickinfo', 'created_at')
    list_filter = ('is_published', 'show_on_quickinfo', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author__first_name')

    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (_('Main Info'), {
            'fields': ('title', 'slug', 'category', 'author', 'is_published', 'show_on_quickinfo')
        }),
        (_('Content & Description'), {
            'fields': ('content',)
        }),
        (_('Media & Attachments'), {
            'fields': ('logo', 'quickinfo_image', 'attached_file', 'video_url')
        }),
        (_('Links'), {
            'fields': ('original_link',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.show_on_quickinfo:
            Resource.objects.exclude(pk=obj.pk).filter(show_on_quickinfo=True).update(show_on_quickinfo=False)
        super().save_model(request, obj, form, change)