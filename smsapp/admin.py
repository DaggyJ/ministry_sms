from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Category, Contact, SMSLog
from .utils import get_celcom_balance
from django.utils.html import format_html

# ----------------------------
# CATEGORY ADMIN
# ----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# ----------------------------
# CONTACT ADMIN
# ----------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'phone')

# ----------------------------
# SMSLOG ADMIN WITH BALANCE
# ----------------------------
@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipients', 'message', 'sent_at', 'status', 'check_balance')
    search_fields = ('sender__username', 'recipient', 'message')

    def check_balance(self, obj):
        return format_html('<a href="{}">Check Balance</a>', '/admin/check-balance/')
    check_balance.short_description = "Balance"

# ----------------------------
# CUSTOM ADMIN VIEW TO FETCH BALANCE
# ----------------------------
def check_balance_view(request):
    balance = get_celcom_balance()
    messages.info(request, f"Current Celcom Balance: {balance}")
    return redirect('/admin/smsapp/smslog/')

# ----------------------------
# Add the admin view safely
# ----------------------------
original_get_urls = admin.site.get_urls  # save original method

def get_urls():
    urls = [
        path('check-balance/', check_balance_view, name='check_balance'),
    ]
    return urls + original_get_urls()  # append original URLs

admin.site.get_urls = get_urls
