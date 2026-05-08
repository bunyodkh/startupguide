from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0014_customfield_field_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='label_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Question'),
        ),
        migrations.AddField(
            model_name='customfield',
            name='label_ru',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Question'),
        ),
        migrations.AddField(
            model_name='customfield',
            name='label_uz',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Question'),
        ),
    ]
