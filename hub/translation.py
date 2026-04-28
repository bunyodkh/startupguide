from modeltranslation.translator import register, TranslationOptions
from .models import EntityCategory, EcosystemEntity, Region


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(EntityCategory)
class EntityCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(EcosystemEntity)
class EcosystemEntityTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name', 'description', 'city')