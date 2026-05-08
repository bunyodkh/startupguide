from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0011_alter_programcycle_contributors_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_open', models.BooleanField(default=False, verbose_name='Accepting Registrations')),
                ('ask_phone', models.BooleanField(default=True, verbose_name='Ask Phone')),
                ('ask_role', models.BooleanField(default=True, help_text='e.g. Student, Entrepreneur, Researcher', verbose_name='Ask Role')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cycle', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='registration_form', to='hub.programcycle', verbose_name='Cycle')),
            ],
            options={
                'verbose_name': 'Registration Form',
                'verbose_name_plural': 'Registration Forms',
            },
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, verbose_name='Question')),
                ('is_required', models.BooleanField(default=False, verbose_name='Required')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='hub.registrationform', verbose_name='Form')),
            ],
            options={
                'verbose_name': 'Custom Field',
                'verbose_name_plural': 'Custom Fields',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='RegistrationResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Full Name')),
                ('email', models.EmailField(verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=50, verbose_name='Phone')),
                ('role', models.CharField(blank=True, max_length=255, verbose_name='Role')),
                ('custom_answers', models.JSONField(blank=True, default=dict, verbose_name='Answers')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='hub.registrationform', verbose_name='Form')),
            ],
            options={
                'verbose_name': 'Registration Response',
                'verbose_name_plural': 'Registration Responses',
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='registrationresponse',
            constraint=models.UniqueConstraint(fields=['form', 'email'], name='unique_response_per_form'),
        ),
    ]
