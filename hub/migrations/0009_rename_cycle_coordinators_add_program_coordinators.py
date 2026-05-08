from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0008_move_details_to_cycle'),
        ('users', '0004_builderprofile_gender'),
    ]

    operations = [
        migrations.RenameField(
            model_name='programcycle',
            old_name='coordinators',
            new_name='contributors',
        ),
        migrations.AddField(
            model_name='ecosystementity',
            name='coordinators',
            field=models.ManyToManyField(
                blank=True,
                help_text='People who coordinate this program.',
                related_name='coordinated_programs',
                to='users.builderprofile',
                verbose_name='Coordinators',
            ),
        ),
    ]
