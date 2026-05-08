from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0013_registrationform_external_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='field_type',
            field=models.CharField(
                choices=[('text', 'Short answer'), ('textarea', 'Long answer')],
                default='text',
                max_length=20,
                verbose_name='Answer type',
            ),
        ),
    ]
