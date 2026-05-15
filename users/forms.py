from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllauthSignupForm, LoginForm as AllauthLoginForm

from .models import BuilderProfile


class CustomSignupForm(AllauthSignupForm):
    first_name = forms.CharField(
        max_length=150,
        label=_('First Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Anvar'),
            'autocomplete': 'first-name',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        label=_('Last Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Anvarov'),
            'autocomplete': 'last-name',
        }),
    )

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

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


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


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Anvar'),
                'autocomplete': 'given-name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Anvarov'),
                'autocomplete': 'family-name',
            }),
        }


class BuilderProfileForm(forms.ModelForm):
    class Meta:
        model = BuilderProfile
        fields = ['photo', 'position', 'bio', 'linkedin_url', 'telegram_handle', 'gender', 'affiliated_entities', 'is_expert', 'expertise']
        widgets = {
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'position': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('e.g. Founder, Investor, Program Manager'),
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input',
                'placeholder': _('Tell others about yourself, your expertise, and how you can help.'),
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://linkedin.com/in/yourname',
            }),
            'telegram_handle': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('durov (without @)'),
            }),
            'affiliated_entities': forms.SelectMultiple(attrs={'class': 'form-input'}),
            'expertise': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-input',
                'placeholder': _('e.g. Product development, fundraising, go-to-market strategy'),
            }),
        }
        labels = {
            'affiliated_entities': _("Affiliated Organizations"),
        }
