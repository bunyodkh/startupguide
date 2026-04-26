from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecosystementity',
            name='coordinators',
            field=models.ManyToManyField(
                blank=True,
                help_text='People (builders) responsible for this program/entity.',
                related_name='coordinated_entities',
                to='users.builderprofile',
                verbose_name='Coordinators',
            ),
        ),
    ]
