# accounts/views.py
from django.views.generic import FormView, View
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .forms import SignUpForm, LoginForm, ResetPinForm, VerifyPinForm, UserCreationForm, CustomSetPasswordForm
from django.contrib.auth import get_user_model
from .models import PinReset
import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


# ---------------------------
# Sign Up View
# ---------------------------
class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        redirect_url = reverse('smsapp:dashboard')

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Account created successfully!',
                'redirect_url': redirect_url
            })

        messages.success(self.request, "Account created successfully!")
        return redirect(redirect_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'errors': errors
            })
        return super().form_invalid(form)


# ---------------------------
# Login View
# ---------------------------
class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        redirect_url = reverse('smsapp:dashboard')

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Logged in successfully!',
                'redirect_url': redirect_url
            })

        return redirect(redirect_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = form.errors.as_json()
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials',
                'errors': errors
            })
        return super().form_invalid(form)


# ---------------------------
# Logout View
# ---------------------------
class LogoutView(View):
    def get(self, request):
        logout(request)
        redirect_url = reverse('accounts:login')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        return redirect(redirect_url)


# ---------------------------
# Reset PIN View
# ---------------------------
class ResetPinView(FormView):
    template_name = 'accounts/reset_pin.html'
    form_class = ResetPinForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Email not found'})
            messages.error(self.request, "Email not found")
            return redirect('accounts:reset_pin')

        code = f"{random.randint(100000, 999999)}"
        PinReset.objects.create(user=user, code=code)

        send_mail(
            subject="Your PIN reset code",
            message=f"Your 6-digit PIN reset code is: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        redirect_url = reverse('accounts:verify_pin')

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"6-digit code sent to {email}",
                'redirect_url': redirect_url
            })

        messages.success(self.request, f"6-digit code sent to {email}")
        return redirect(redirect_url)


# ---------------------------
# Verify PIN View
# ---------------------------
class VerifyPinView(FormView):
    template_name = 'accounts/verify_pin.html'
    form_class = VerifyPinForm

    def form_valid(self, form):
        code = form.cleaned_data['code']
        try:
            pin = PinReset.objects.get(code=code, verified=False)
        except PinReset.DoesNotExist:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid code'})
            messages.error(self.request, "Invalid code")
            return redirect('accounts:verify_pin')

        if pin.created_at < timezone.now() - timedelta(minutes=10):
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Code expired'})
            messages.error(self.request, "Code expired")
            return redirect('accounts:reset_pin')

        pin.verified = True
        pin.save()
        self.request.session['reset_user_id'] = pin.user.id

        redirect_url = reverse('accounts:set_new_password')

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Code verified! You can now reset your password.',
                'redirect_url': redirect_url
            })

        messages.success(self.request, "Code verified! You can now reset your password.")
        return redirect(redirect_url)


# ---------------------------
# Set New Password View
# ---------------------------
class SetNewPasswordView(FormView):
    template_name = 'accounts/set_new_password.html'
    form_class = CustomSetPasswordForm

    # Pass the user instance to the form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.request.session.get('reset_user_id')
        if not user_id:
            kwargs['user'] = None
        else:
            kwargs['user'] = User.objects.get(id=user_id)
        return kwargs

    def form_valid(self, form):
        form.save()  # Saves the new password
        self.request.session.pop('reset_user_id', None)  # Clear session

        redirect_url = reverse('accounts:login')

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Password reset successfully!',
                'redirect_url': redirect_url
            })

        messages.success(self.request, "Password reset successfully!")
        return redirect(redirect_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'errors': errors
            })
        return super().form_invalid(form)