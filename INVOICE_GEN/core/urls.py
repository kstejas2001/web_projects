from django.urls import path
from . import views
from .views import home_redirect, client_list, add_client, item_list, add_item, add_invoice, add_invoice_items, user_login, register_user

urlpatterns = [
    path('', home_redirect, name='home'),
    path('clients/', client_list, name='client_list'),
    path('clients/add', add_client, name='add_client'),
    path('items/', item_list, name='item_list'),
    path('items/add', add_item, name='add_item'),
    path('invoices/add', add_invoice, name='add_invoice'),
    path('invoices/<int:invoice_id>/items', add_invoice_items, name='add_invoice_items'),
    path('login/', user_login, name='login'),
]
from .views import register_user, admin_home, staff_home, user_logout, invoice_list, invoice_detail, download_invoice_pdf, toggle_invoice_status, client_invoices, client_report_pdf, edit_client, delete_client, edit_item, delete_item

urlpatterns += [
    path('register/<str:role>/', register_user, name='register'),
    path('admin-home/', admin_home, name='admin_home'),
    path('staff-home/', staff_home, name='staff_home'),
    path('logout/', user_logout, name='logout'),
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/pdf/', download_invoice_pdf, name='download_invoice_pdf'),
    path('invoices/<int:invoice_id>/toggle-status/', toggle_invoice_status, name='toggle_invoice_status'),
    path('clients/<int:client_id>/invoices/', client_invoices, name='client_invoices'),
    path('clients/<int:client_id>/report/', client_report_pdf, name='client_report_pdf'),
    path('clients/<int:client_id>/edit/', edit_client, name='edit_client'),
    path('clients/<int:client_id>/delete/', delete_client, name='delete_client'),
    path('items/<int:item_id>/edit/', edit_item, name='edit_item'),
    path('items/<int:item_id>/delete/', delete_item, name='delete_item'),
]
