from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ProgramCycle, RegistrationForm


class CycleForm(forms.ModelForm):
    class Meta:
        model = ProgramCycle
        fields = ('title', 'description', 'status', 'start_date', 'end_date', 'registration_deadline', 'cover_image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'registration_deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class RegistrationSettingsForm(forms.ModelForm):
    class Meta:
        model = RegistrationForm
        fields = ('is_open', 'external_url')
        widgets = {
            'external_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://',
            }),
        }
