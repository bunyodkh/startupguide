import os
from io import BytesIO
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

from config.utils import UploadToPath


def _unique_profile_slug(base, exclude_pk=None):
    slug = slugify(base)[:200] or 'person'
    qs = BuilderProfile.objects.all()
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    if not qs.filter(slug=slug).exists():
        return slug
    n = 2
    while qs.filter(slug=f"{slug}-{n}").exists():
        n += 1
    return f"{slug}-{n}"


class BuilderProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='builder_profile',
        verbose_name=_("User")
    )

    photo = ProcessedImageField(
        upload_to=UploadToPath('avatars'),
        processors=[ResizeToFit(800, 800)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name=_("Profile Photo"),
        help_text=_("Recommended size: square image, e.g., 500x500px.")
    )

    photo_thumbnail = models.ImageField(
        upload_to=UploadToPath('avatars/thumbnails'),
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Profile Photo Thumbnail"),
    )

    position = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Role in the Ecosystem"),
        help_text=_("e.g., Tracker, Program Coordinator, Fund Partner")
    )

    bio = models.TextField(
        blank=True,
        verbose_name=_("Bio and Expertise"),
        help_text=_("Describe your experience, project focus, and how you can help.")
    )

    linkedin_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("LinkedIn URL")
    )

    telegram_handle = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Telegram Username"),
        help_text=_("Without @, e.g., durov")
    )

    class Gender(models.TextChoices):
        MALE = 'male', _("Male")
        FEMALE = 'female', _("Female")
        NA = 'na', _("Not Specified")

    gender = models.CharField(
        max_length=6,
        choices=Gender.choices,
        default=Gender.NA,
        verbose_name=_("Gender")
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Published on site"),
        help_text=_("Uncheck to temporarily hide the profile from the public catalog")
    )

    show_on_main_page = models.BooleanField(
        default=False,
        verbose_name=_("Show on Main Page"),
        help_text=_("If checked, this builder will be featured on the main landing page.")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Creation Date")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Update Date")
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("Leave blank to auto-generate from name.")
    )

    affiliated_entities = models.ManyToManyField(
        'hub.EcosystemEntity',
        blank=True,
        related_name='affiliated_builders',
        verbose_name=_("Affiliated Organizations"),
        help_text=_("Select the universities, incubators, or programs this builder is involved with.")
    )

    class Meta:
        verbose_name = _("Builder Profile")
        verbose_name_plural = _("Builder Profiles")
        ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_photo = self.photo.name if self.photo else None

    def save(self, *args, **kwargs):
        if not self.slug:
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            base = full_name or self.user.username
            self.slug = _unique_profile_slug(base, exclude_pk=self.pk)
        old_photo = self._original_photo
        old_thumbnail = self.photo_thumbnail.name if self.photo_thumbnail else None

        super().save(*args, **kwargs)

        current_photo = self.photo.name if self.photo else None
        if current_photo != old_photo:
            if old_photo:
                self._delete_file(old_photo)
            if old_thumbnail:
                self._delete_file(old_thumbnail)
            if self.photo:
                self._generate_thumbnail()
            self._original_photo = current_photo

    def _generate_thumbnail(self):
        from PIL import Image
        img = Image.open(self.photo)
        img = img.convert('RGB')
        img.thumbnail((150, 150), Image.LANCZOS)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=80)

        base = os.path.splitext(os.path.basename(self.photo.name))[0]
        thumb_name = f"{base}_thumb.jpg"
        self.photo_thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
        BuilderProfile.objects.filter(pk=self.pk).update(photo_thumbnail=self.photo_thumbnail.name)

    def _delete_file(self, name):
        from django.core.files.storage import default_storage
        if name and default_storage.exists(name):
            default_storage.delete(name)

    def __str__(self):
        full_name = self.user.get_full_name()
        if full_name:
            return f"{full_name} — {self.position}"
        return f"{self.user.username} — {self.position}"

    def get_absolute_url(self):
        return reverse('users:view_profile', kwargs={'slug': self.slug})

    @property
    def get_photo_url(self):
        if self.photo and self.photo.storage.exists(self.photo.name):
            return self.photo.url
        from django.templatetags.static import static
        if self.gender == self.Gender.FEMALE:
            return static('images/default-favatar.png')
        return static('images/default-avatar.png')

    @property
    def get_thumbnail_url(self):
        if self.photo_thumbnail and self.photo_thumbnail.storage.exists(self.photo_thumbnail.name):
            return self.photo_thumbnail.url
        return self.get_photo_url
