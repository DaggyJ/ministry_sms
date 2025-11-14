from django.urls import path
from .views import DashboardView, UploadContactsView, GetPastorsView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('upload/', UploadContactsView.as_view(), name='upload_contacts'),
    path('get_pastors/', GetPastorsView.as_view(), name='get_pastors'),
]

    