from django.contrib import admin
from .models import Client
from .models import Item
from .models import Invoice
from .models import InvoiceItem
from .models import UserProfile

# Register your models here.
admin.site.register(Client)
admin.site.register(Item)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(UserProfile)