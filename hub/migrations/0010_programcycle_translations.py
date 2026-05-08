from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0009_rename_cycle_coordinators_add_program_coordinators'),
    ]

    operations = [
        migrations.AddField(
            model_name='programcycle',
            name='title_en',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='programcycle',
            name='title_uz',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='programcycle',
            name='title_ru',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='programcycle',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
        migrations.AddField(
            model_name='programcycle',
            name='description_uz',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
        migrations.AddField(
            model_name='programcycle',
            name='description_ru',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
    ]
