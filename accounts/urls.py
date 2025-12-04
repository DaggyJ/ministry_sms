# accounts/urls.py
from django.urls import path
from .views import SignUpView, LoginView, LogoutView, ResetPinView, VerifyPinView, SetNewPasswordView

app_name = "accounts"  # <-- REQUIRED for namespacing

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset-pin/', ResetPinView.as_view(), name='reset_pin'),
    path('verify-pin/', VerifyPinView.as_view(), name='verify_pin'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set_new_password'),
]
