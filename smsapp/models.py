# smsapp/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Contact(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.phone})"

# New Pastor model
class Pastor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    region = models.CharField(max_length=100, blank=True, null=True)
    subregion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
