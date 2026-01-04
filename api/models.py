from django.db import models


class Transaction(models.Model):
    """Optional: Store C2B transactions for audit and duplicate detection."""
    
    trans_id = models.CharField(max_length=100, unique=True, db_index=True)
    business_short_code = models.CharField(max_length=20)
    bill_ref_number = models.CharField(max_length=100)
    trans_amount = models.DecimalField(max_digits=10, decimal_places=2)
    msisdn = models.CharField(max_length=20)
    trans_time = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('pending', 'Pending'),
        ],
        default='pending'
    )
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['trans_id']),
        ]
    
    def __str__(self):
        return f"{self.trans_id} - {self.bill_ref_number} - {self.trans_amount}"
