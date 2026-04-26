from modeltranslation.translator import register, TranslationOptions
from .models import EntityCategory, EcosystemEntity

@register(EntityCategory)
class EntityCategoryTranslationOptions(TranslationOptions):
    # Указываем поля для перевода (slug переводить не нужно, он один для всех языков)
    fields = ('name',)

@register(EcosystemEntity)
class EcosystemEntityTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name', 'description', 'city')