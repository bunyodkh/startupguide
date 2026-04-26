from django import forms
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllauthSignupForm, LoginForm as AllauthLoginForm

from .models import BuilderProfile


class CustomSignupForm(AllauthSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': _('you@example.com'),
            'autocomplete': 'email',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        })


class CustomLoginForm(AllauthLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': _('you@example.com'),
            'autocomplete': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })


class BuilderProfileForm(forms.ModelForm):
    class Meta:
        model = BuilderProfile
        fields = ['photo', 'position', 'bio', 'linkedin_url', 'telegram_handle', 'affiliated_entities']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'affiliated_entities': forms.SelectMultiple(),
        }
        labels = {
            'affiliated_entities': _("Affiliated Organizations"),
        }
