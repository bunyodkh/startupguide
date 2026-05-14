from django.db import migrations, models
from django.utils.text import slugify


def populate_entity_slugs(apps, schema_editor):
    EcosystemEntity = apps.get_model('hub', 'EcosystemEntity')
    used = set()
    for entity in EcosystemEntity.objects.order_by('pk'):
        base = slugify(entity.name or 'program')[:200] or 'program'
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        entity.slug = slug
        entity.save(update_fields=['slug'])
        used.add(slug)


def populate_cycle_slugs(apps, schema_editor):
    ProgramCycle = apps.get_model('hub', 'ProgramCycle')
    used = set()
    for cycle in ProgramCycle.objects.select_related('program').order_by('pk'):
        title = cycle.title or ''
        program_name = cycle.program.name or ''
        base = slugify(title or f"{program_name}-{cycle.cycle_number}")[:200] or f'cycle-{cycle.pk}'
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        cycle.slug = slug
        cycle.save(update_fields=['slug'])
        used.add(slug)


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0015_customfield_label_translations'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecosystementity',
            name='slug',
            field=models.SlugField(blank=True, db_index=False, default='', max_length=255, verbose_name='Slug'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='programcycle',
            name='slug',
            field=models.SlugField(blank=True, db_index=False, default='', max_length=255, verbose_name='Slug'),
            preserve_default=False,
        ),
        migrations.RunPython(populate_entity_slugs, migrations.RunPython.noop),
        migrations.RunPython(populate_cycle_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='ecosystementity',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True, verbose_name='Slug', help_text='Leave blank to auto-generate from name.'),
        ),
        migrations.AlterField(
            model_name='programcycle',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True, verbose_name='Slug', help_text='Leave blank to auto-generate.'),
        ),
    ]
