from django.urls import path
from .views import (
    SignUpView, LoginView, LogoutView, ResetPinView, VerifyPinView, SetNewPasswordView, 
    UserStatusView, manage_users_page, admin_users_list
)

app_name = "accounts"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset-pin/', ResetPinView.as_view(), name='reset_pin'),
    path('verify-pin/', VerifyPinView.as_view(), name='verify_pin'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set_new_password'),
    path('user-status/', UserStatusView.as_view(), name='user_status'),
    path('manage-users/', manage_users_page, name='manage_users_page'),
    path('admin-users-list/', admin_users_list, name='admin_users_list'),
]

