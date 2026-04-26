import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ComplexityValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError(_("Password must contain at least one letter."))
        if not re.search(r'\d', password):
            raise ValidationError(_("Password must contain at least one number."))
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;\'`~/]', password):
            raise ValidationError(_("Password must contain at least one special character."))

    def get_help_text(self):
        return _("Your password must contain at least one letter, one number, and one special character.")
