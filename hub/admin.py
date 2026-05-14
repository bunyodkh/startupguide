from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from modeltranslation.admin import TabbedTranslationAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import EntityCategory, EcosystemEntity, Region, ProgramCycle, RegistrationForm, CustomField, RegistrationResponse, Community


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


class ProgramCycleInline(TabularInline):
    model = ProgramCycle
    extra = 0
    fields = ('cycle_number', 'title', 'status', 'start_date', 'end_date', 'registration_deadline', 'is_active')
    ordering = ('-cycle_number',)
    readonly_fields = ('cycle_number',)


@admin.register(ProgramCycle)
class ProgramCycleAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('__str__', 'program', 'cycle_number', 'status', 'start_date', 'end_date', 'registration_deadline', 'is_active')
    list_filter = ('status', 'is_active', 'program')
    search_fields = ('program__name', 'title')
    autocomplete_fields = ['program', 'organizers']
    filter_horizontal = ('contributors', 'regions')

    fieldsets = (
        (_("Cycle"), {
            'fields': ('program', 'cycle_number', 'title', 'description', 'status', 'is_active', 'is_featured'),
        }),
        (_("Dates"), {
            'fields': ('start_date', 'end_date', 'registration_deadline'),
        }),
        (_("Media"), {
            'fields': ('cover_image',),
        }),
        (_("People & Places"), {
            'fields': ('organizers', 'contributors', 'regions', 'address'),
        }),
    )


@admin.register(EcosystemEntity)
class EcosystemEntityAdmin(ModelAdmin, TabbedTranslationAdmin):
    inlines = [ProgramCycleInline]
    list_display = ('get_logo', 'name', 'category', 'city', 'is_active')
    list_display_links = ('get_logo', 'name')
    list_filter = ('category', 'is_active', 'has_physical_space')
    search_fields = ('name', 'short_name', 'category__name')
    autocomplete_fields = ['parent', 'category']

    filter_horizontal = ('coordinators',)

    fieldsets = (
        (_("General"), {
            'fields': ('name', 'short_name', 'category', 'parent', 'description', 'website', 'is_active'),
        }),
        (_("Media"), {
            'fields': ('logo',),
        }),
        (_("Location"), {
            'fields': ('has_physical_space', 'city'),
        }),
        (_("People"), {
            'fields': ('coordinators',),
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


class CustomFieldInline(TabularInline):
    model = CustomField
    extra = 1
    fields = ('label', 'is_required', 'order')


@admin.register(RegistrationForm)
class RegistrationFormAdmin(ModelAdmin):
    list_display = ('__str__', 'is_open', 'ask_phone', 'ask_role', 'response_count')
    list_filter = ('is_open',)
    search_fields = ('cycle__program__name', 'cycle__title')
    inlines = [CustomFieldInline]

    fieldsets = (
        (_("Form"), {
            'fields': ('cycle', 'is_open'),
        }),
        (_("Fixed Fields"), {
            'fields': ('ask_phone', 'ask_role'),
        }),
    )

    def response_count(self, obj):
        return obj.responses.count()
    response_count.short_description = _("Responses")


@admin.register(RegistrationResponse)
class RegistrationResponseAdmin(ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'role', 'submitted_at')
    list_filter = ('form__cycle__program',)
    search_fields = ('full_name', 'email')
    readonly_fields = ('form', 'full_name', 'email', 'phone', 'role', 'custom_answers', 'submitted_at')


@admin.register(Community)
class CommunityAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'short_title', 'slug', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'short_title')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('coordinators', 'members', 'supporting_organizations')
    fieldsets = (
        (_("Identity"), {
            'fields': ('title', 'short_title', 'slug', 'description'),
        }),
        (_("Media"), {
            'fields': ('logo', 'cover_image'),
        }),
        (_("Contact"), {
            'fields': ('website', 'telegram_handle'),
        }),
        (_("People & Organizations"), {
            'fields': ('coordinators', 'members', 'supporting_organizations'),
        }),
        (_("Settings"), {
            'fields': ('is_published', 'is_featured'),
        }),
    )
