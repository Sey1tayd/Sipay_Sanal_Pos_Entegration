from django.db import models
from django.utils import timezone

# Create your models here.

class Payment(models.Model):
    """Payment model to track payment attempts and results"""
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('cancelled', 'İptal Edildi'),
        ('processing', 'İşleniyor'),
    ]
    
    invoice_id = models.CharField(max_length=100, unique=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=3, default='TRY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    md_status = models.CharField(max_length=10, blank=True, null=True)
    sipay_status = models.CharField(max_length=10, blank=True, null=True)
    status_code = models.CharField(max_length=10, blank=True, null=True)
    status_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
    
    def __str__(self):
        return f"{self.invoice_id} - {self.status}"
