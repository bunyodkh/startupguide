from django.db import models
from django.utils.translation import gettext_lazy as _


class TechnicalAnnouncement(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Technical Announcement")
        verbose_name_plural = _("Technical Announcements")
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CallToActionAnnouncement(models.Model):
    message = models.TextField(verbose_name=_("Message"))
    link = models.CharField(
        max_length=500,
        verbose_name=_("Link"),
        help_text=_("Internal path (e.g. /en/programs/) or full external URL.")
    )
    link_text = models.CharField(max_length=100, verbose_name=_("Link Text"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Call to Action Announcement")
        verbose_name_plural = _("Call to Action Announcements")
        ordering = ['-created_at']

    def __str__(self):
        return self.message[:80]
