from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False  # User must be approved by admin before login
        user.status = 'pending'  # Show pending approval
        if commit:
            user.save()
        return user

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
