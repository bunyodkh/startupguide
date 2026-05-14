from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0021_add_address_translation_to_cycle'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='formed_year',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Year Formed'),
        ),
        migrations.AddField(
            model_name='community',
            name='programs',
            field=models.ManyToManyField(
                blank=True,
                help_text='Programs supported or promoted by this community.',
                related_name='supported_by_communities',
                to='hub.ecosystementity',
                verbose_name='Supported Programs',
            ),
        ),
    ]
