from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    BuilderProfile = apps.get_model('users', 'BuilderProfile')
    used = set()
    for profile in BuilderProfile.objects.select_related('user').order_by('pk'):
        full_name = f"{profile.user.first_name} {profile.user.last_name}".strip()
        base = slugify(full_name or profile.user.username)[:200] or f'person-{profile.pk}'
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        profile.slug = slug
        profile.save(update_fields=['slug'])
        used.add(slug)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_builderprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='builderprofile',
            name='slug',
            field=models.SlugField(blank=True, db_index=False, default='', max_length=255, verbose_name='Slug'),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='builderprofile',
            name='slug',
            field=models.SlugField(
                blank=True, max_length=255, unique=True, verbose_name='Slug',
                help_text='Leave blank to auto-generate from name.',
            ),
        ),
    ]
