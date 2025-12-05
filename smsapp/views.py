from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Category, Contact, SMSLog
from .forms import UploadContactsForm
import openpyxl
import json
from .utils import send_sms, get_celcom_balance
from django.contrib import messages  # <-- add this


# ==========================
# Admin-only mixin
# ==========================
class AdminRequiredMixin(UserPassesTestMixin):
    """Allow only admin (staff) users."""
    def test_func(self):
        return self.request.user.is_staff  # or .is_superuser

    def handle_no_permission(self):
        return render(self.request, "smsapp/no_access.html", {
            "message": "Admin access required."
        })


# ==========================
# Celcom Balance View (Admin-only)
# ==========================
class CheckBalanceView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Admin-only view to check Celcom balance."""
    
    login_url = '/accounts/login/'  # redirect if not logged in
    
    def test_func(self):
        return self.request.user.is_staff  # only admin/staff

    def handle_no_permission(self):
        messages.error(self.request, "Admin access required.")
        return redirect('/')  # fallback for non-admin

    def get(self, request, *args, **kwargs):
        balance = get_celcom_balance()
        messages.info(request, f"Current Celcom Balance: {balance}")
        return redirect('smsapp:dashboard')  # redirect back to dashboard


# ==========================
# Get Pastors / Contacts
# ==========================
class GetPastorsView(LoginRequiredMixin, View):
    """Return JSON of contacts for a given category."""
    
    def get(self, request, *args, **kwargs):
        category_param = request.GET.get('category')  # e.g., "Regional", "Subregional", "Pastor"
        contacts = Contact.objects.all()
        
        if category_param:
            contacts = contacts.filter(category__name__iexact=category_param)

        data = [
            {
                'id': c.id,
                'name': c.name,
                'phone': c.phone,
                'region': c.region,
                'subregion': c.subregion,
                'category': c.category.name
            }
            for c in contacts
        ]

        return JsonResponse({'pastors': data})


# ==========================
# Dashboard for Sending SMS
# ==========================


class DashboardView(LoginRequiredMixin, View):
    template_name = "smsapp/dashboard.html"

    def get(self, request):
        """
        Display the dashboard with categories, SMS logs, and optionally Celcom balance.
        """
        categories = Category.objects.all()
        context = {
            "categories": categories,
            "sms_logs": SMSLog.objects.order_by('-sent_at')[:20]  # visible to all users
        }

        # Celcom balance — only staff
        if request.user.is_staff:
            context["celcom_balance"] = get_celcom_balance()

        return render(request, self.template_name, context)

    def post(self, request):
    # Detect JSON
        try:
            data = json.loads(request.body)
            category = data.get("category")
            message = data.get("message", "").strip()
            recipients = data.get("recipients", [])
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid request data"}, status=400)

    # Validation
        if not category:
            return JsonResponse({"status": "error", "message": "Please select a category."})
        if not recipients:
            return JsonResponse({"status": "error", "message": "Please select at least one recipient."})
        if not message:
            return JsonResponse({"status": "error", "message": "Message cannot be empty."})

    # Send SMS
        sender_id = "BELOVEDCHKE"
        result = send_sms(message, recipients, sender_id)

    # Log SMS
        SMSLog.objects.create(
            sender=request.user,
            message=message,
            recipients=", ".join(recipients),
            status=result.get("status", "unknown")
        )

        return JsonResponse({
            "status": result.get("status", "unknown"),
            "message": result.get("message", "SMS sent successfully")
        })



# ==========================
# Upload Contacts (Admin-only)
# ==========================
class UploadContactsView(LoginRequiredMixin, AdminRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = "smsapp/upload_contacts.html"

    def get(self, request):
        form = UploadContactsForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = UploadContactsForm(request.POST, request.FILES)
        message = error = None

        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                added_count = 0

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row[0] and row[1] and row[2]:
                        name, phone, category_name = row[:3]
                        region = row[3] if len(row) > 3 else None
                        subregion = row[4] if len(row) > 4 else None

                        category, _ = Category.objects.get_or_create(name=category_name.strip())
                        Contact.objects.create(
                            name=name.strip(),
                            phone=str(phone).strip(),
                            category=category,
                            region=region.strip() if region else None,
                            subregion=subregion.strip() if subregion else None
                        )
                        added_count += 1

                message = f"{added_count} contacts uploaded successfully!"

            except Exception as e:
                error = f"Error processing file: {str(e)}"
        else:
            error = "Invalid file. Please upload a valid Excel (.xlsx) file."

        return render(
            request,
            self.template_name,
            {"form": form, "message": message, "error": error}
        )
