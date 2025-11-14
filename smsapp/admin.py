from django.contrib import admin
from .models import Category, Contact

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'phone')
