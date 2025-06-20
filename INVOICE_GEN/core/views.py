from django.shortcuts import render
from .models import Client, Item
from .forms import ClientForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        try:
            role = request.user.userprofile.role
            if role == 'admin':
                return redirect('admin_home')
            elif role == 'staff':
                return redirect('staff_home')
        except:
            return redirect('login')
    return render(request, 'home.html')  # Guest page

def client_list(request):
    clients = Client.objects.all()
    return render(request, 'client_list.html', {'clients': clients})

def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'add_client.html', {'form': form})

@login_required
def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client updated successfully.")
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)

    return render(request, 'edit_client.html', {'form': form, 'client': client})

@login_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client deleted successfully.")
        return redirect('client_list')

    return render(request, 'delete_client.html', {'client': client})


def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})

from .forms import ItemForm

def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'add_item.html', {'form': form})

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully.")
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)

    return render(request, 'edit_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('item_list')

    return render(request, 'delete_item.html', {'item': item})


from django.urls import reverse
from .forms import InvoiceForm

def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save() # Redirect to a page to add items to this invoice
            return redirect(reverse('add_invoice_items', args=[invoice.id]))
    else:
        form = InvoiceForm()
    return render(request, 'add_invoice.html', {'form': form})

from .models import Invoice, InvoiceItem
from decimal import Decimal
from .forms import InvoiceItemForm

def add_invoice_items(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    items = invoice.items.all()

    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
           item = form.cleaned_data['item']
           quantity = form.cleaned_data['quantity']
           price = item.price
           gst_rate = item.gst_rate
           gst_amount = (price * quantity * gst_rate) / 100
           total = (price * quantity) + gst_amount

           InvoiceItem.objects.create(
               invoice=invoice,
               item=item,
               quantity=quantity,
               price=price,
               gst_amount=round(gst_amount, 2),
               total=round(total, 2)
           )
           return redirect('add_invoice_items', invoice_id=invoice.id)
        else:
            # Recalculate total if form is invalid
            subtotal = sum(i.price * i.quantity for i in items)
            total_gst = sum(i.gst_amount for i in items)
            grand_total = sum(i.total for i in items)

            return render(request, 'add_invoice_items.html', {
                'invoice': invoice,
                'items': items,
                'form': form,
                'subtotal': subtotal,
                'total_gst': total_gst,
                'grand_total': grand_total
            })
    else:
        # GET request - show empty form
        form = InvoiceItemForm()
        subtotal = sum(i.price * i.quantity for i in items)
        total_gst = sum(i.gst_amount for i in items)
        grand_total = sum(i.total for i in items)

        return render(request, 'add_invoice_items.html', {
            'invoice': invoice,
            'items': items,
            'form': form,
            'subtotal': subtotal,
            'total_gst': total_gst,
            'grand_total': grand_total
        })
    
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import UserProfile

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role == 'admin':
                    return redirect('admin_home')
                elif profile.role == 'staff':
                    return redirect('staff_home')
            except UserProfile.DoesNotExist:
                logout(request)
                return render(request, 'login.html', {'error': 'No role assigned. Contact admin.'})
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

from django.contrib.auth.models import User
from .models import UserProfile

def register_user(request, role):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already taken.',
                'role': role
            })

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, role=role)

        return redirect('login')

    return render(request, 'register.html', {'role': role})

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
import calendar
import json
from .models import Client, Item, Invoice, InvoiceItem

@login_required
def admin_home(request):
    total_clients = Client.objects.count()
    total_items = Item.objects.count()
    total_invoices = Invoice.objects.count()
    total_revenue = InvoiceItem.objects.aggregate(Sum('total'))['total__sum'] or 0

    # Monthly stats
    invoices_by_month = Invoice.objects.annotate(month=TruncMonth('date')).values('month').annotate(count=Count('id')).order_by('month')
    revenue_by_month = InvoiceItem.objects.annotate(month=TruncMonth('invoice__date')).values('month').annotate(total=Sum('total')).order_by('month')

    # Format for Chart.js
    month_labels = []
    invoice_counts = []
    revenue_totals = []

    for i in range(1, 13):
        label = calendar.month_name[i]
        month_labels.append(label)
        month_data = next((item for item in invoices_by_month if item['month'].month == i), None)
        revenue_data = next((item for item in revenue_by_month if item['month'].month == i), None)
        invoice_counts.append(month_data['count'] if month_data else 0)
        revenue_totals.append(float(revenue_data['total']) if revenue_data else 0)

    return render(request, 'admin_home.html', {
        'total_clients': total_clients,
        'total_items': total_items,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'month_labels': json.dumps(month_labels),
        'invoice_counts': json.dumps(invoice_counts),
        'revenue_totals': json.dumps(revenue_totals),
    })

@login_required
def staff_home(request):
    return render(request, 'staff_home.html')

from django.contrib.auth import logout

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

from django.db.models import Q
from datetime import datetime

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().select_related('client')

    # Filtering logic
    client_id = request.GET.get('client')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if client_id and client_id != 'all':
        invoices = invoices.filter(client__id=client_id)

    if status and status != 'all':
        is_paid = True if status == 'paid' else False
        invoices = invoices.filter(is_paid=is_paid)

    if start_date:
        invoices = invoices.filter(date__gte=start_date)
    if end_date:
        invoices = invoices.filter(date__lte=end_date)

    clients = Client.objects.all()

    return render(request, 'invoice_list.html', {
        'invoices': invoices,
        'clients': clients,
        'selected_client': client_id,
        'selected_status': status,
        'start_date': start_date,
        'end_date': end_date,
    })

from django.shortcuts import get_object_or_404

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()  # uses related_name='items'
    
    subtotal = sum(i.price * i.quantity for i in items)
    total_gst = sum(i.gst_amount for i in items)
    grand_total = sum(i.total for i in items)

    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'subtotal': subtotal,
        'total_gst': total_gst,
        'grand_total': grand_total,
    })

@login_required
def client_invoices(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    invoices = Invoice.objects.filter(client=client)

    return render(request, 'client_invoices.html', {
        'client': client,
        'invoices': invoices,
    })

@login_required
def client_report_pdf(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    invoices = Invoice.objects.filter(client=client)

    # You can summarize totals here if needed
    total_invoices = invoices.count()
    total_amount = sum(i.total_amount for i in invoices)

    # PDF setup
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, f"Client Report: {client.name}")
    y -= 20

    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"GST Number: {client.gst_number}")
    y -= 15
    p.drawString(40, y, f"State: {client.state}")
    y -= 30

    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, y, f"Total Invoices: {total_invoices}")
    p.drawString(240, y, f"Total Amount: Rs. {total_amount:.2f}")
    y -= 30

    # Table Headers
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Invoice No")
    p.drawString(150, y, "Date")
    p.drawString(240, y, "Status")
    p.drawString(320, y, "Amount")
    y -= 10
    p.line(40, y, width - 40, y)
    y -= 15

    p.setFont("Helvetica", 10)
    for i in invoices:
        if y < 100:  # New page if needed
            p.showPage()
            y = height - 40
        p.drawString(40, y, i.invoice_number)
        p.drawString(150, y, str(i.date))
        p.drawString(240, y, "Paid" if i.is_paid else "Unpaid")
        p.drawString(320, y, f"{i.total_amount:.2f}")
        y -= 15

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


from django.contrib import messages

@login_required
def toggle_invoice_status(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.is_paid = not invoice.is_paid  # Toggle
    invoice.save()

    status = "Paid" if invoice.is_paid else "Unpaid"
    messages.success(request, f"Invoice marked as {status}.")
    return redirect('invoice_detail', invoice_id=invoice.id)


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from django.http import HttpResponse
import io

@login_required
def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()

    subtotal = sum(i.price * i.quantity for i in items)
    total_gst = sum(i.gst_amount for i in items)
    grand_total = sum(i.total for i in items)

    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40

    # Header
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, y, "FAMILY SUPERMARKET")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, "Nagashiva Complex, 7th Road, K R Nagar - 571602")
    y -= 15
    p.drawCentredString(width / 2, y, "Ph: 8086582400 | Email: fmlissupermarket@gmail.com")
    y -= 15
    p.drawCentredString(width / 2, y, f"GSTIN: 29DHEPK9036G1ZZ | State: Karnataka [29]")

    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, f"Invoice No: {invoice.invoice_number}")
    p.drawRightString(width - 40, y, f"Date: {invoice.date}")
    y -= 20

    # Client
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Customer: {invoice.client.name if invoice.client else 'Cash A/c'}")
    y -= 20

    # Table headers
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Sl")
    p.drawString(60, y, "Item Name")
    p.drawString(200, y, "Qty")
    p.drawString(240, y, "Rate")
    p.drawString(290, y, "Amount")
    y -= 10
    p.line(40, y, width - 40, y)
    y -= 10

    p.setFont("Helvetica", 10)
    for idx, i in enumerate(items, start=1):
        p.drawString(40, y, str(idx))
        p.drawString(60, y, i.item.name)
        p.drawString(200, y, f"{i.quantity:.2f}")
        p.drawString(240, y, f"{i.price:.2f}")
        p.drawString(290, y, f"{i.total:.2f}")
        y -= 15

    y -= 10
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(width - 40, y, f"NET PAYABLE: Rs. {grand_total:.2f}")

    y -= 40

    # Tax Summary
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Tax Details:")
    y -= 15
    p.setFont("Helvetica", 10)
    p.drawString(40, y, "TAXABLE AMT")
    p.drawString(130, y, "CGST%")
    p.drawString(180, y, "CGST AMT")
    p.drawString(240, y, "SGST%")
    p.drawString(290, y, "SGST AMT")
    y -= 15

    p.drawString(40, y, f"{(subtotal):.2f}")
    p.drawString(130, y, "2.5")
    p.drawString(180, y, f"{(total_gst / 2):.2f}")
    p.drawString(240, y, "2.5")
    p.drawString(290, y, f"{(total_gst / 2):.2f}")

    y -= 30
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Payment Details:")
    y -= 15
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Net Payable: Rs. {grand_total:.2f}")
    p.drawString(200, y, "Cash")

    y -= 30
    p.setFont("Helvetica-Bold", 11)
    # p.drawCentredString(width / 2, y, "You saved Rs. 21.00")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, "Thank you, Visit Again!")

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')