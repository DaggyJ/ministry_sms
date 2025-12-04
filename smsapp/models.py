# smsapp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Contact(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    # Add optional region and subregion fields
    region = models.CharField(max_length=100, blank=True, null=True)
    subregion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

# Pastor model
class Pastor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    region = models.CharField(max_length=100, blank=True, null=True)
    subregion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class SMSLog(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <-- use this
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    recipients = models.CharField(max_length=15)
    sent_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20)
    

    def __str__(self):
        return f"SMS sent by {self.sender} on {self.sent_at}"