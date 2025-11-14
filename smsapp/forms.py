from django import forms

class UploadContactsForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")
