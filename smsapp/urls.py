from django.urls import path
from . import views
from .views import DashboardView, UploadContactsView, GetPastorsView, CheckBalanceView


app_name = "smsapp"

urlpatterns = [
    path('upload/', UploadContactsView.as_view(), name='upload_contacts'),
    path('get_pastors/', GetPastorsView.as_view(), name='get_pastors'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('check-balance/', CheckBalanceView.as_view(), name='check_balance'),
    path('sms_logs/', DashboardView.as_view(), name='sms_logs'),
    



]

    