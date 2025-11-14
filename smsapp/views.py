from django.views import View
from .utils import send_sms
from django.shortcuts import render, redirect
from .models import Category, Contact
from .forms import UploadContactsForm
import openpyxl
from django.http import JsonResponse
from .models import Pastor  # make sure you have this model

class GetPastorsView(View):
    def get(self, request, *args, **kwargs):
        category = request.GET.get('category')
        pastors = Pastor.objects.all()

        # Filter by category
        if category == 'Regional':
            pastors = pastors.filter(region__isnull=False)  # adjust field if needed
        elif category == 'Subregional':
            pastors = pastors.filter(subregion__isnull=False)
        # else: show all pastors for "Pastors" tab

        data = [{'id': p.id, 'name': p.name, 'phone': p.phone} for p in pastors]
        return JsonResponse({'pastors': data})



class DashboardView(View):
    template_name = "smsapp/dashboard.html"

    def get(self, request):
        """Display the form with all categories."""
        categories = Category.objects.all()
        return render(request, self.template_name, {"categories": categories})

    def post(self, request):
        """Handle form submission and send SMS."""
        categories = Category.objects.all()
        message = request.POST.get("message")
        category_id = request.POST.get("category")

        try:
            category = Category.objects.get(id=category_id)
            recipients = [c.phone for c in Contact.objects.filter(category=category)]

            # Placeholder credentials (we’ll replace with Celcom’s)
            api_key = "YOUR_API_KEY"
            sender_id = "BELOVEDCHURCH"

            result = send_sms(api_key, sender_id, message, recipients)
            context = {"categories": categories, "result": result}
        except Category.DoesNotExist:
            context = {"categories": categories, "result": {"error": "Invalid category selected."}}
        except Exception as e:
            context = {"categories": categories, "result": {"error": str(e)}}

        return render(request, self.template_name, context)


class UploadContactsView(View):
    template_name = "smsapp/upload_contacts.html"

    def get(self, request):
        """Display the upload form."""
        form = UploadContactsForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Handle the uploaded Excel file and save contacts."""
        form = UploadContactsForm(request.POST, request.FILES)
        message = error = None

        if form.is_valid():
            excel_file = request.FILES['excel_file']

            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                # Expect columns: Name | Phone | Category
                added_count = 0
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row[0] and row[1] and row[2]:  # Ensure Name, Phone, Category are present
                        name, phone, category_name = row
                        category, _ = Category.objects.get_or_create(name=category_name.strip())
                        Contact.objects.create(name=name.strip(), phone=str(phone).strip(), category=category)
                        added_count += 1

                message = f"{added_count} contacts uploaded successfully!"

            except Exception as e:
                error = f"Error processing file: {str(e)}"

        else:
            error = "Invalid file. Please upload a valid Excel (.xlsx) file."

        return render(request, self.template_name, {"form": form, "message": message, "error": error})