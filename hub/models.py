import os
from io import BytesIO
from django.db import models, transaction
from django.urls import reverse
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

from config.utils import UploadToPath


def _unique_slug(model_class, base, exclude_pk=None):
    slug = slugify(base)[:200] or 'item'
    qs = model_class.objects.all()
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    if not qs.filter(slug=slug).exists():
        return slug
    n = 2
    while qs.filter(slug=f"{slug}-{n}").exists():
        n += 1
    return f"{slug}-{n}"


class Region(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("Slug")
    )

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")
        ordering = ['name']

    def __str__(self):
        return self.name


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

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("Leave blank to auto-generate from name.")
    )

    category = models.ForeignKey(
        EntityCategory,
        on_delete=models.PROTECT,
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

    coordinators = models.ManyToManyField(
        'users.BuilderProfile',
        blank=True,
        related_name='coordinated_programs',
        verbose_name=_("Coordinators"),
        help_text=_("People who coordinate this program.")
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

    show_on_main = models.BooleanField(
        default=False,
        verbose_name=_("Featured on main page"),
        help_text=_("Show this entity in the featured block on the home page. Only active entities will be shown.")
    )

    class Meta:
        verbose_name = _("Ecosystem Entity")
        verbose_name_plural = _("Ecosystem Entities")
        ordering = ['category__name', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_logo = self.logo.name if self.logo else None

    def save(self, *args, **kwargs):
        if not self.slug:
            base = getattr(self, 'name_en', None) or self.name
            self.slug = _unique_slug(EcosystemEntity, base, exclude_pk=self.pk)
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
        if self.has_physical_space:
            return reverse('hub:place_detail', kwargs={'slug': self.slug})
        return reverse('hub:view_program', kwargs={'slug': self.slug})


class ProgramCycle(models.Model):

    class ProgramStatus(models.TextChoices):
        UPCOMING    = 'upcoming',    _("Upcoming")
        ACCEPTING   = 'accepting',   _("Registration")
        IN_PROGRESS = 'in_progress', _("In Progress")
        COMPLETED   = 'completed',   _("Completed")
        CANCELLED   = 'cancelled',   _("Cancelled")

    program = models.ForeignKey(
        EcosystemEntity,
        on_delete=models.CASCADE,
        related_name='cycles',
        verbose_name=_("Program")
    )

    cycle_number = models.PositiveIntegerField(
        blank=True,
        verbose_name=_("Cycle Number"),
        help_text=_("Auto-assigned if left blank.")
    )

    title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Title"),
        help_text=_("Optional label, e.g. 'Cohort 3' or 'Spring 2024'")
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("Leave blank to auto-generate.")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Cycle-specific description or notes.")
    )

    status = models.CharField(
        max_length=20,
        choices=ProgramStatus.choices,
        blank=True,
        verbose_name=_("Status")
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Start Date")
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("End Date")
    )

    registration_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Registration Deadline")
    )

    cover_image = ProcessedImageField(
        upload_to=UploadToPath('covers/cycles'),
        processors=[ResizeToFit(1200, 630)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name=_("Cover Image"),
        help_text=_("Recommended: 1200×630px.")
    )

    organizers = models.ManyToManyField(
        EcosystemEntity,
        blank=True,
        symmetrical=False,
        related_name='organized_cycles',
        verbose_name=_("Organizers"),
        help_text=_("Organizations that run or host this cycle.")
    )

    contributors = models.ManyToManyField(
        'users.BuilderProfile',
        blank=True,
        related_name='contributed_cycles',
        verbose_name=_("Contributors"),
        help_text=_("People contributing to this specific cycle.")
    )

    regions = models.ManyToManyField(
        Region,
        blank=True,
        related_name='cycles',
        verbose_name=_("Regions"),
        help_text=_("Regions covered by this cycle.")
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Event Address"),
        help_text=_("Physical venue or address for this cycle.")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured on main page"),
        help_text=_("Show this cycle in the featured block on the home page.")
    )

    class Meta:
        verbose_name = _("Program Cycle")
        verbose_name_plural = _("Program Cycles")
        ordering = ['-cycle_number']
        unique_together = [('program', 'cycle_number')]

    def save(self, *args, **kwargs):
        if not self.cycle_number:
            with transaction.atomic():
                last = ProgramCycle.objects.select_for_update().filter(program=self.program).order_by('-cycle_number').first()
                self.cycle_number = (last.cycle_number + 1) if last else 1
        if not self.slug:
            title = getattr(self, 'title_en', None) or self.title
            program_name = getattr(self.program, 'name_en', None) or self.program.name
            base = title or f"{program_name}-{self.cycle_number}"
            self.slug = _unique_slug(ProgramCycle, base, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        label = self.title or f"#{self.cycle_number}"
        return f"{self.program.name} — {label}"

    @property
    def display_label(self):
        return self.title or f"#{self.cycle_number}"

    @property
    def days_until_deadline(self):
        if not self.registration_deadline:
            return None
        return (self.registration_deadline - timezone.now().date()).days

    @property
    def registration_open(self):
        days = self.days_until_deadline
        return days is not None and days >= 0

    @property
    def deadline_label(self):
        days = self.days_until_deadline
        if days is None:
            return None
        if days > 1:
            return _("%(days)d days left") % {'days': days}
        if days == 1:
            return _("Last day to apply!")
        if days == 0:
            return _("Closes today")
        return _("Reg. closed")

    @property
    def deadline_verbose(self):
        days = self.days_until_deadline
        if days is None:
            return None
        if days > 1:
            return _("%(days)d days left till the end of registration") % {'days': days}
        if days == 1:
            return _("Last day to apply!")
        if days == 0:
            return _("Registration closes today")
        return _("Registration closed")

    def get_absolute_url(self):
        url = self.program.get_absolute_url()
        return f"{url}?cycle={self.slug}" if self.slug else url

    @property
    def duration_display(self):
        if not self.start_date and not self.end_date:
            return None

        def fmt(date, include_year):
            month = date.strftime("%b")
            day = date.day
            return f"{month} {day}, {date.year}" if include_year else f"{month} {day}"

        if self.start_date and self.end_date:
            if self.start_date.year == self.end_date.year:
                return f"{fmt(self.start_date, False)} – {fmt(self.end_date, False)}, {self.end_date.year}"
            return f"{fmt(self.start_date, True)} – {fmt(self.end_date, True)}"
        if self.start_date:
            return _("%(date)s") % {'date': fmt(self.start_date, True)}
        return _("Until %(date)s") % {'date': fmt(self.end_date, True)}


class Community(models.Model):

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title")
    )

    short_title = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Short Title / Abbreviation")
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("Leave blank to auto-generate from title.")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    logo = ProcessedImageField(
        upload_to=UploadToPath('logos/communities'),
        processors=[ResizeToFit(800, 800)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name=_("Logo")
    )

    logo_thumbnail = models.ImageField(
        upload_to=UploadToPath('logos/communities/thumbnails'),
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Logo Thumbnail")
    )

    cover_image = ProcessedImageField(
        upload_to=UploadToPath('covers/communities'),
        processors=[ResizeToFit(1200, 630)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name=_("Cover Image"),
        help_text=_("Recommended: 1200×630px.")
    )

    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Website")
    )

    telegram_handle = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Telegram Channel / Group"),
        help_text=_("Without @, e.g., mycomminity")
    )

    formed_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Year Formed")
    )

    coordinators = models.ManyToManyField(
        'users.BuilderProfile',
        blank=True,
        related_name='coordinated_communities',
        verbose_name=_("Coordinators")
    )

    members = models.ManyToManyField(
        'users.BuilderProfile',
        blank=True,
        related_name='communities',
        verbose_name=_("Members"),
        help_text=_("Individual people who are part of this community.")
    )

    supporting_organizations = models.ManyToManyField(
        EcosystemEntity,
        blank=True,
        related_name='supporting_communities',
        verbose_name=_("Supporting Organizations"),
        help_text=_("Organizations that support this community.")
    )

    programs = models.ManyToManyField(
        EcosystemEntity,
        blank=True,
        related_name='supported_by_communities',
        verbose_name=_("Supported Programs"),
        help_text=_("Programs supported or promoted by this community.")
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Published")
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured on main page"),
        help_text=_("Show this community in the featured block on the home page.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")
        ordering = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_logo = self.logo.name if self.logo else None

    def save(self, *args, **kwargs):
        if not self.slug:
            base = getattr(self, 'title_en', None) or self.title
            self.slug = _unique_slug(Community, base, exclude_pk=self.pk)
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
        Community.objects.filter(pk=self.pk).update(logo_thumbnail=self.logo_thumbnail.name)

    def __str__(self):
        return self.short_title or self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('hub:community_detail', kwargs={'slug': self.slug})

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


class RegistrationForm(models.Model):
    cycle = models.OneToOneField(
        ProgramCycle,
        on_delete=models.CASCADE,
        related_name='registration_form',
        verbose_name=_("Cycle"),
    )
    is_open = models.BooleanField(
        default=False,
        verbose_name=_("Accepting Registrations"),
    )
    external_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("External Registration URL"),
        help_text=_("If set, shows a button to this URL instead of the built-in form."),
    )
    ask_phone = models.BooleanField(
        default=True,
        verbose_name=_("Ask Phone"),
    )
    ask_role = models.BooleanField(
        default=True,
        verbose_name=_("Ask Role"),
        help_text=_("e.g. Student, Entrepreneur, Researcher"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Registration Form")
        verbose_name_plural = _("Registration Forms")

    def __str__(self):
        return f"{self.cycle} — Form"


class CustomField(models.Model):

    class FieldType(models.TextChoices):
        TEXT     = 'text',     _("Short answer")
        TEXTAREA = 'textarea', _("Long answer")

    form = models.ForeignKey(
        RegistrationForm,
        on_delete=models.CASCADE,
        related_name='custom_fields',
        verbose_name=_("Form"),
    )
    label = models.CharField(
        max_length=255,
        verbose_name=_("Question"),
    )
    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        default=FieldType.TEXT,
        verbose_name=_("Answer type"),
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Required"),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
    )

    class Meta:
        verbose_name = _("Custom Field")
        verbose_name_plural = _("Custom Fields")
        ordering = ['order']

    def __str__(self):
        return self.label


class RegistrationResponse(models.Model):
    form = models.ForeignKey(
        RegistrationForm,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_("Form"),
    )
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_("Phone"))
    role = models.CharField(max_length=255, blank=True, verbose_name=_("Role"))
    custom_answers = models.JSONField(default=dict, blank=True, verbose_name=_("Answers"))
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Registration Response")
        verbose_name_plural = _("Registration Responses")
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(fields=['form', 'email'], name='unique_response_per_form'),
        ]

    def __str__(self):
        return f"{self.full_name} — {self.form.cycle}"
