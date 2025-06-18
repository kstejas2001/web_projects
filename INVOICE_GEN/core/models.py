from django.db import models

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    state = models.CharField(max_length=50)
    gst_number = models.CharField(max_length=15, null=False, blank=False)
    
    def __str__(self):
        return self.name

# item Model
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

# invoice Model
class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    invoice_number = models.CharField(max_length=20, unique=True)
    state = models.CharField(max_length=50)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client.name}"
    
    @property
    def total_amount(self):
        return sum(item.total for item in self.items.all())


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # item price at the time
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2) # price * quantity + gst_amount

    def __str__(self):
        return f"{self.item.name} x {self.quantity} (Invoice #{self.invoice.invoice_number})"

from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
