from django import forms
from .models import Client
import re
from django.core.exceptions import ValidationError

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'address', 'state', 'gst_number']

    def clean_gst_number(self):
        gst = self.cleaned_data.get('gst_number')
        if gst:
            pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'

            if not re.match(pattern, gst):
                raise ValidationError("Invalid GST number format. Please enter a valid GST number. Example: 12ABCDE1234F1Z5")
            return gst
        else:
            raise ValidationError("GST number is required.")
        
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'gst_rate']

from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_number', 'state', 'is_paid']

from .models import InvoiceItem

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item', 'quantity']