from modeltranslation.translator import register, TranslationOptions
from .models import ResourceCategory, Resource

@register(ResourceCategory)
class ResourceCategoryTranslationOptions(TranslationOptions):
    # Переводим название категории и её описание
    fields = ('name', 'description')

@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    # Переводим заголовок ресурса и сам контент/описание
    fields = ('title', 'content')