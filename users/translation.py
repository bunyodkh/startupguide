from modeltranslation.translator import register, TranslationOptions
from .models import BuilderProfile

@register(BuilderProfile)
class BuilderProfileTranslationOptions(TranslationOptions):
    fields = ('position', 'bio')