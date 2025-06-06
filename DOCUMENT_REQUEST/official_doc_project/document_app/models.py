from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DocumentRequest(models.Model):
    DOCUMENT_CHOICES = [
        ('Aadhaar', 'Aadhaar Card'),
        ('PAN', 'PAN Card'),
        ('VoterID', 'Voter ID'),
        ('RationCard', 'Ration Card'),
        ('Birth Certificate', 'Birth Certificate'),
        ('Marriage Certificate', 'Marriage Certificate'),
        ('Passport', 'Passport'),
        ('Death Certificate', 'Death Certificate'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)

    # Ration card
    family_head = models.CharField(max_length=100, null=True, blank=True)
    card_type = models.CharField(max_length=50, null=True, blank=True)
    ration_members = models.TextField(null=True, blank=True)

    # Birth certificate fields
    child_name = models.CharField(max_length=100, null=True, blank=True)
    birth_time = models.CharField(max_length=20, null=True, blank=True)
    place_of_birth = models.CharField(max_length=100, null=True, blank=True)
    mother_name = models.CharField(max_length=100, null=True, blank=True)

    # Death certificate fields
    deceased_name = models.CharField(max_length=100, null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    death_time = models.CharField(max_length=20, null=True, blank=True)
    place_of_death = models.CharField(max_length=100, null=True, blank=True)
    relation_to_deceased = models.CharField(max_length=100, null=True, blank=True)

    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_CHOICES)
    id_proof = models.FileField(upload_to='id_proofs/')
    address_proof = models.FileField(upload_to='address_proofs/')
    status = models.CharField(max_length=20, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.document_type}"
    
    status = models.CharField(max_length=20, default='Pending')
    admin_remarks = models.TextField(blank=True, null=True)
    final_document = models.FileField(upload_to='final_docs/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class DownloadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_request = models.ForeignKey(DocumentRequest, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downloaded {self.document_request.document_type} on {self.downloaded_at}"
