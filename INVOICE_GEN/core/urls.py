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
from .views import register_user, admin_home, staff_home, user_logout, invoice_list, invoice_detail

urlpatterns += [
    path('register/<str:role>/', register_user, name='register'),
    path('admin-home/', admin_home, name='admin_home'),
    path('staff-home/', staff_home, name='staff_home'),
    path('logout/', user_logout, name='logout'),
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
]
