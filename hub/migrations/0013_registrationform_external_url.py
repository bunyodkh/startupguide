from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0012_registrationform_customfield_registrationresponse'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationform',
            name='external_url',
            field=models.URLField(
                blank=True,
                null=True,
                verbose_name='External Registration URL',
                help_text='If set, shows a button to this URL instead of the built-in form.',
            ),
        ),
    ]
