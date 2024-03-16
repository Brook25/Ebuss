from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreation
from django.core import (RegexValidator, MaxLengthValidator,
            MinLengthValidator

class UserCreationForm(BaseUserCreation):
    first_name = forms.CharField(required=True,
            validators=[RegexValidator(
                regex=r'^[A-Z][a-z]$',
                message='First name must start with a Capital letter,
                and the rest of the characters must be small letters.'
            )])
    last_name = forms.CharField(required=True,
            validators=[RegexValidator(
                regex=r'^[A-Z][a-z]$',
                message='First name must start with a Capital letter,
                and the rest of the characters must be small letters.'
            )])
    birth_date = forms.DateField(input_formats=['%Y-%m-%d'])
