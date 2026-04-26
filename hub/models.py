import os
from io import BytesIO
from django.db import models
from django.urls import reverse
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

from config.utils import UploadToPath


class EntityCategory(models.Model):
    name = models.CharField(
        max_length=100, 
        verbose_name=_("Name")
    )

    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Slug (URL identifying name)"),
        help_text=_("Leave blank to auto-generate")
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('hub:category_detail', kwargs={'slug': self.slug})


class EcosystemEntity(models.Model):

    name = models.CharField(
        max_length=255, 
        verbose_name=_("Name")
    )
    
    category = models.ForeignKey(
        EntityCategory,
        on_delete=models.PROTECT, # Запрещаем удалять категорию, если к ней уже привязаны организации!
        related_name='entities',
        verbose_name=_("Category")
    )


    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_("Parent Organization"),
        help_text=_("E.g., An incubator belongs to a university.")
    )

    organizers = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='organized_entities',
        verbose_name=_("Organizers"),
        help_text=_("Organizations that run or host this program/entity.")
    )

    coordinators = models.ManyToManyField(
        'users.BuilderProfile',
        blank=True,
        related_name='coordinated_entities',
        verbose_name=_("Coordinators"),
        help_text=_("People (builders) responsible for this program/entity.")
    )

    has_physical_space = models.BooleanField(
        default=True,
        verbose_name=_("Has Physical Space"),
        help_text=_("Uncheck this if it is a purely virtual program.")
    )

    short_name = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name=_("Abbreviation / Short Name")
    )
    
    description = models.TextField(
        blank=True, 
        verbose_name=_("Description")
    )
    
    city = models.CharField(
        max_length=100, 
        default=_("Tashkent"), 
        verbose_name=_("City")
    )
    
    website = models.URLField(
        blank=True, 
        null=True, 
        verbose_name=_("Website")
    )
    
    logo = ProcessedImageField(
        upload_to=UploadToPath('logos/entities'),
        processors=[ResizeToFit(800, 800)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name=_("Logo")
    )

    logo_thumbnail = models.ImageField(
        upload_to=UploadToPath('logos/entities/thumbnails'),
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Logo Thumbnail"),
    )

    founded_year = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name=_("Founded Year")
    )
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_("Is Active")
    )

    class Meta:
        verbose_name = _("Ecosystem Entity")
        verbose_name_plural = _("Ecosystem Entities")
        ordering = ['category__name', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_logo = self.logo.name if self.logo else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        current_logo = self.logo.name if self.logo else None
        if self.logo and current_logo != self._original_logo:
            self._generate_thumbnail()
            self._original_logo = current_logo

    def _generate_thumbnail(self):
        from PIL import Image
        img = Image.open(self.logo)
        img = img.convert('RGB')
        img.thumbnail((150, 150), Image.LANCZOS)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        base = os.path.splitext(os.path.basename(self.logo.name))[0]
        self.logo_thumbnail.save(f"{base}_thumb.jpg", ContentFile(thumb_io.getvalue()), save=False)
        EcosystemEntity.objects.filter(pk=self.pk).update(logo_thumbnail=self.logo_thumbnail.name)

    @property
    def get_logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        from django.templatetags.static import static
        return static('images/default-logo.png')

    @property
    def get_thumbnail_url(self):
        if self.logo_thumbnail and hasattr(self.logo_thumbnail, 'url'):
            return self.logo_thumbnail.url
        return self.get_logo_url

    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.parent.short_name or self.parent.name})"
        return self.name

    def get_absolute_url(self):
        return reverse('hub:entity_detail', kwargs={'pk': self.pk})
