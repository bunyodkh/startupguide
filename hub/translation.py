from modeltranslation.translator import register, TranslationOptions
from .models import EntityCategory, EcosystemEntity, ProgramCycle, Region, CustomField


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(EntityCategory)
class EntityCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(EcosystemEntity)
class EcosystemEntityTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name', 'description', 'city')


@register(ProgramCycle)
class ProgramCycleTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(CustomField)
class CustomFieldTranslationOptions(TranslationOptions):
    fields = ('label',)