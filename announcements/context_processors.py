from .models import TechnicalAnnouncement, CallToActionAnnouncement


def announcements(request):
    return {
        'technical_announcement': TechnicalAnnouncement.objects.filter(is_active=True).first(),
        'cta_announcement': CallToActionAnnouncement.objects.filter(is_active=True).first(),
    }
