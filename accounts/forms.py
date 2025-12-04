# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email')

class ResetPinForm(forms.Form):
    email = forms.EmailField()

class VerifyPinForm(forms.Form):
    code = forms.CharField(max_length=6)

class CustomSetPasswordForm(SetPasswordForm):
    """
    SetPasswordForm requires a user instance. 
    This form is compatible with our custom User model.
    """
    pass  # Inherits all validations from SetPasswordForm