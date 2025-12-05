# accounts/views.py
import json
import random
from datetime import timedelta
from django.views import View
from django.views.generic import FormView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import (
    SignUpForm,
    LoginForm,
    ResetPinForm,
    VerifyPinForm,
    CustomSetPasswordForm
)
from .models import PinReset, CustomUser

User = get_user_model()


# ---------------------------
# Sign Up View
# ---------------------------
class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm

    def form_valid(self, form):
        # Create user but do NOT activate immediately
        user = form.save(commit=False)
        user.is_active = False  # User cannot login until admin approval
        user.save()

        redirect_url = reverse('accounts:login')  # Redirect to login after registration

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Account created successfully! Awaiting admin approval.',
                'redirect_url': redirect_url
            })

        messages.success(self.request, "Account created successfully! Awaiting admin approval.")
        return redirect(redirect_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'error': 'Validation failed', 'errors': errors})
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
            return JsonResponse({'success': True, 'message': 'Logged in successfully!', 'redirect_url': redirect_url})

        return redirect(redirect_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'error': 'Invalid credentials', 'errors': errors})
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
# Reset PIN Views
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
            return JsonResponse({'success': True, 'message': f"6-digit code sent to {email}", 'redirect_url': redirect_url})

        messages.success(self.request, f"6-digit code sent to {email}")
        return redirect(redirect_url)


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
            return JsonResponse({'success': True, 'message': 'Code verified! You can now reset your password.', 'redirect_url': redirect_url})

        messages.success(self.request, "Code verified! You can now reset your password.")
        return redirect(redirect_url)


class SetNewPasswordView(FormView):
    template_name = 'accounts/set_new_password.html'
    form_class = CustomSetPasswordForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.request.session.get('reset_user_id')
        kwargs['user'] = User.objects.get(id=user_id) if user_id else None
        return kwargs

    def form_valid(self, form):
        form.save()
        self.request.session.pop('reset_user_id', None)
        redirect_url = reverse('accounts:login')

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Password reset successfully!', 'redirect_url': redirect_url})

        messages.success(self.request, "Password reset successfully!")
        return redirect(redirect_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'error': 'Validation failed', 'errors': errors})
        return super().form_invalid(form)


# ---------------------------
# Admin User Management Views
# ---------------------------
@method_decorator(csrf_exempt, name='dispatch')
class UserStatusView(UserPassesTestMixin, View):
    """
    Handles approving, disabling, enabling, and rejecting users.
    Expects JSON body: { "user_id": <id>, "action": "approve|disable|enable|reject" }
    """
    def test_func(self):
        return self.request.user.is_admin

    def post(self, request):
        data = json.loads(request.body)
        user_id = data.get("user_id")
        action = data.get("action")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"status": "User not found"}, status=404)

        if action == 'approve':
            user.status = 'approved'
            user.is_active = True  # Activate account for login
            user.save()
            return JsonResponse({"status": "User approved successfully"})

        elif action == 'enable':
            user.status = 'approved'
            user.is_active = True
            user.save()
            return JsonResponse({"status": "User enabled successfully"})

        elif action == 'disable':
            if user.is_admin:
                return JsonResponse({"status": "Cannot disable admin"}, status=400)
            user.status = 'disabled'
            user.is_active = False  # Deactivate account to prevent login
            user.save()
            return JsonResponse({"status": "User disabled successfully"})

        elif action == 'reject':
            user.delete()
            return JsonResponse({"status": "User rejected and removed"})

        else:
            return JsonResponse({"status": "Invalid action"}, status=400)




@login_required
@user_passes_test(lambda u: u.is_admin)
def manage_users_page(request):
    """
    Render the admin page for managing users.
    Only accessible by admin users.
    """
    return render(request, "accounts/manage_users.html")


@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_users_list(request):
    """
    Returns a JSON list of all users for admin management.
    """
    users = CustomUser.objects.all().values("id", "username", "status")
    return JsonResponse({"users": list(users)})

