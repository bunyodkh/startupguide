from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class ResourceCategory(models.Model):
    """
    Категории базы знаний (например: Reports, Templates, Guides).
    """
    name = models.CharField(
        max_length=100, 
        verbose_name=_("Category Name")
    )
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Slug")
    )
    description = models.TextField(
        blank=True, 
        verbose_name=_("Description")
    )

    class Meta:
        verbose_name = _("Resource Category")
        verbose_name_plural = _("Resource Categories")
        ordering = ['name']

    def __str__(self):
        return self.name


class Resource(models.Model):
    """
    Универсальная модель для любого полезного материала (отчет, гайд, видео, шаблон).
    """
    title = models.CharField(
        max_length=255, 
        verbose_name=_("Title")
    )
    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        verbose_name=_("URL Slug")
    )
    category = models.ForeignKey(
        ResourceCategory, 
        on_delete=models.PROTECT, 
        related_name='resources',
        verbose_name=_("Category")
    )
    
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='authored_resources',
        verbose_name=_("Author")
    )
    
    content = models.TextField(
        verbose_name=_("Content / Description"),
        help_text=_("Main text of the article, or a detailed description if this is a downloadable file/video.")
    )
    
    attached_file = models.FileField(
        upload_to='wiki/files/', 
        blank=True, 
        null=True, 
        verbose_name=_("Attached File"),
        help_text=_("e.g., PDF report, Excel template, or presentation.")
    )
    video_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name=_("Video URL"),
        help_text=_("YouTube or Vimeo link.")
    )
    
    is_published = models.BooleanField(
        default=False, 
        verbose_name=_("Is Published")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Creation Date")
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_("Update Date")
    )

    class Meta:
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")
        ordering = ['-created_at']

    def __str__(self):
        return self.title