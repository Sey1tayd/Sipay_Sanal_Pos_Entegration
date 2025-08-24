from django.contrib import admin
from .models import Payment

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice_id', 'order_id', 'total', 'currency_code', 'status', 'md_status', 'sipay_status', 'created_at']
    list_filter = ['status', 'currency_code', 'md_status', 'sipay_status', 'created_at']
    search_fields = ['invoice_id', 'order_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('invoice_id', 'order_id', 'total', 'currency_code', 'status')
        }),
        ('3D Secure Bilgileri', {
            'fields': ('md_status', 'sipay_status', 'status_code', 'status_description')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
