from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required
import datetime

from django.contrib.auth.decorators import login_required
from .models import UserProfile

def home(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'admin':
                return redirect(request, 'document_app/admin_home.html')  # Admin home page
            else:
                return render(request, 'document_app/user_home.html')  # User homepage
        except UserProfile.DoesNotExist:
            return render(request, 'document_app/home.html')  # fallback guest view
    return render(request, 'document_app/home.html')  # Guest homepage

@login_required
def admin_home(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'admin':
        return redirect(request, 'document_app/home.html')
    return render(request, 'document_app/admin_home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render('register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        UserProfile.objects.create(user=user, role='user')  # Create a UserProfile for the new user

        return redirect('home')  # Redirect to home after registration
    return render(request, 'document_app/register.html')

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def user_settings(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, 'Profile updated successfully.')
    
    return render(request, 'document_app/user_settings.html')

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
                return redirect('admin_home')  # Redirect to admin home if user is admin
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
        total_requests = all_requests.count()
        pending_requests = all_requests.filter(status='Pending').count()
        approved_requests = all_requests.filter(status='Approved').count()
        rejected_requests = all_requests.filter(status='Rejected').count()

        return render(request, 'document_app/admin_dashboard.html', {'all_requests': all_requests, 'total_requests': total_requests, 'pending_requests': pending_requests, 'approved_requests': approved_requests, 'rejected_requests': rejected_requests})
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
        full_name=request.POST['full_name']
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        address = request.POST['address']
        document_type = request.POST['document_type']
        id_proof = request.FILES['id_proof']
        address_proof = request.FILES['address_proof']

        # Create DocumentRequest object
        doc_request = DocumentRequest.objects.create(
            user=request.user,
            full_name=full_name,
            dob=dob,
            gender=gender,
            address=address,
            document_type=document_type,
            id_proof=id_proof,
            address_proof=address_proof,
        )

        # if PAN Card, store father_name
        if document_type == "PAN Card":
            doc_request.father_name = request.POST.get('father_name')

        # if RationCard, store additional fields
        if document_type == "RationCard":
            doc_request.family_head = request.POST.get('family_head')
            doc_request.card_type = request.POST.get('card_type')
            doc_request.ration_members = request.POST.get('ration_members')

        if document_type == "BirthCertificate":
            doc_request.child_name = request.POST.get('child_name')
            doc_request.birth_time = request.POST.get('birth_time')
            doc_request.place_of_birth = request.POST.get('place_of_birth')
            doc_request.mother_name = request.POST.get('mother_name')

        if document_type == "DeathCertificate":
            doc_request.deceased_name = request.POST.get('deceased_name')
            doc_request.death_date = request.POST.get('death_date')
            doc_request.death_time = request.POST.get('death_time')
            doc_request.place_of_death = request.POST.get('place_of_death')
            doc_request.relation_to_deceased = request.POST.get('relation_to_deceased')


        doc_request.save()  # Save the updated fields
        return redirect('home') # Redirect to home after request submission
    return render(request, 'document_app/request_form.html')

from .utils.certificate_generation import generate_certificate

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

        if status == 'Approved':
            # Auto-generate the PDF here
            if doc_request.document_type == "PAN Card" and not doc_request.pan_number:
                import random
                import string
                prefix = ''.join(random.choices(string.ascii_uppercase, k=5))
                digits = ''.join(random.choices(string.digits, k=4))
                suffix = random.choice(string.ascii_uppercase)
                doc_request.pan_number = f"{prefix}{digits}{suffix}"

            # Prepare user data for certificate generation
            user_data = {
                'full_name': doc_request.full_name,
                'dob': doc_request.dob.strftime('%d-%m-%Y') if doc_request.dob else 'N/A',
                'gender': doc_request.gender if doc_request.gender else 'N/A',
                'address': doc_request.address if doc_request.address else 'N/A',
                'father_name': doc_request.father_name if doc_request.father_name else 'N/A',
                'aadhaar_number': f"XXXX-XXXX-{str(doc_request.id).zfill(4)}",
                'pan_number': doc_request.pan_number if doc_request.pan_number else 'N/A',
                'user_id': str(doc_request.user.id),
                'request_id': doc_request.id,

                 # Ration-specific fields
                'family_head': doc_request.family_head or 'N/A',
                'card_type': doc_request.card_type or 'N/A',
                'ration_members': doc_request.ration_members.strip().split('\n') if doc_request.ration_members else [],

                # Birth certificate specific fields
                'birth_time': doc_request.birth_time or 'N/A',
                'child_name': doc_request.child_name or 'N/A',
                'place_of_birth': doc_request.place_of_birth or 'N/A',
                'mother_name': doc_request.mother_name or 'N/A',

                # Death certificate specific fields
                'deceased_name': doc_request.deceased_name or 'N/A',
                'death_date': doc_request.death_date.strftime('%d-%m-%Y') if doc_request.death_date else 'N/A',
                'death_time': doc_request.death_time or 'N/A',
                'place_of_death': doc_request.place_of_death or 'N/A',
                'relation_to_deceased': doc_request.relation_to_deceased or 'N/A',

            }           
            generate_certificate(user_data, doc_request.document_type, doc_request)
            doc_request.save()
            return redirect('admin_panel')
        elif status == 'Rejected':
            if not remarks.strip():
                messages.error(request, "Please provide a reason for rejection")
                return render(request, 'document_app/update_request.html', {'doc_request': doc_request})
            doc_request.final_document = None
            doc_request.save()
            return redirect('admin_panel')
        
    return render(request, 'document_app/update_request.html', {'doc_request': doc_request})

from django.contrib.auth.decorators import login_required

@login_required
def track_status(request):
    requests = DocumentRequest.objects.filter(user=request.user)
    return render(request, 'document_app/track_status.html', {'requests': requests})