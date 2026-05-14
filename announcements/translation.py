from modeltranslation.translator import register, TranslationOptions
from .models import TechnicalAnnouncement, CallToActionAnnouncement


@register(TechnicalAnnouncement)
class TechnicalAnnouncementTranslationOptions(TranslationOptions):
    fields = ('title', 'message')


@register(CallToActionAnnouncement)
class CallToActionAnnouncementTranslationOptions(TranslationOptions):
    fields = ('message', 'link_text')
