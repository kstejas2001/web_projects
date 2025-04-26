from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'document_app/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        UserProfile.objects.create(user=user, role='user')  # Create a UserProfile for the new user

        return redirect('home')  # Redirect to home after registration
    return render(request, 'document_app/register.html')

from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Get or create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if profile.role == 'admin':
                return redirect('admin_panel')  # Redirect to admin panel if user is admin
            else:
                return redirect('home')  # Regular user home
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'document_app/login.html')

@login_required
def admin_panel(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role == 'admin':
        all_requests = DocumentRequest.objects.all().order_by('-submitted_at')  # Get all document requests
        return render(request, 'document_app/admin_dashboard.html', {'all_requests': all_requests})
    else:
        return redirect('home') # prevent non-admin users from accessing admin dashboard

from django.contrib.auth import logout
def logout_view(request):
        logout(request)
        return redirect('home')  # Redirect to home after logout

from .models import DocumentRequest
from django.contrib.auth.decorators import login_required

@login_required
def request_document(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        document_type = request.POST['document_type']
        id_proof = request.FILES['id_proof']
        address_proof = request.FILES['address_proof']

        # Create DocumentRequest object
        DocumentRequest.objects.create(
            user=request.user,
            full_name=full_name,
            document_type=document_type,
            id_proof=id_proof,
            address_proof=address_proof,
        )
        
        return redirect('home') # Redirect to home after request submission
    return render(request, 'document_app/request_form.html')

@login_required
def update_request(request, request_id):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'admin':
        return redirect('home') # prevent non-admin users from accessing this view
    
    doc_request = DocumentRequest.objects.get(id=request_id)

    if request.method == 'POST':
        status = request.POST['status']
        remarks = request.POST.get('remarks', '')
        final_doc = request.FILES.get('final_document')

        doc_request.status = status
        doc_request.admin_remarks = remarks

        if final_doc:
            doc_request.final_document = final_doc
            
            doc_request.save()
            return redirect('admin_panel')
        
    return render(request, 'document_app/update_request.html', {'doc_request': doc_request})

from django.contrib.auth.decorators import login_required

@login_required
def track_status(request):
    requests = DocumentRequest.objects.filter(user=request.user)
    return render(request, 'document_app/track_status.html', {'requests': requests})