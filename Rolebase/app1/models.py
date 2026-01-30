from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
import uuid

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICE =[
        ("admin",'admin'),
        ("patient","patient"),
        ("staff","staff"),
    ]
    role =models.CharField(max_length=100,choices=ROLE_CHOICE)

class AdminProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    admin_code=models.CharField(max_length=50)

class patientProfile(models.Model):
    user=models.OneToOneField(User,related_name='patient',on_delete=models.CASCADE)
    medical_history=models.CharField(null=True,blank=True)
    insurance_number=models.CharField(max_length=100)

class staffProfile(models.Model):
    user=models.OneToOneField(User,related_name='staff',on_delete=models.CASCADE)
    employee_id=models.CharField(max_length=50,unique=True)
    department=models.CharField(max_length=100)
    STAFF_TYPE_CHOICES = [
        ("doctor", "Doctor"),
        ("nurse", "Nurse"),
        ("accountant", "Accountant"),
        ("lab", "Lab Technician"),
        ("admin", "Admin Staff"),
    ]
    staff_type = models.CharField(
        max_length=50,
        choices=STAFF_TYPE_CHOICES,
        default="nurse" 
    )
    def __str__(self):
        return f"{self.user.username} ({self.staff_type})"

class DoctorProfile(models.Model):
    staff = models.OneToOneField(staffProfile,on_delete=models.CASCADE,related_name="doctor")
    specialization =models.CharField( max_length=50)
    license_number =models.CharField(max_length=100,unique=True)
    hospital_name=models.CharField(max_length=100)

class AccountantProfile(models.Model):
    staff = models.OneToOneField(staffProfile, related_name='accountant', on_delete=models.CASCADE)
    accounting_certification = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.IntegerField(default=0)

    def __str__(self):
        return f"Accountant: {self.staff.user.username}"
    
class NurseProfile(models.Model):
    staff = models.OneToOneField(staffProfile, on_delete=models.CASCADE, related_name="nurse")

    license_number = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    Nurse_choices=[
            ("day", "Day"),
            ("night", "Night"),
            ("rotational", "Rotational"),
        ]
    shift = models.CharField(
        max_length=20,
        choices=Nurse_choices
    )
    years_of_experience = models.PositiveIntegerField(default=0)


class LabTechnicianProfile(models.Model):
    staff = models.OneToOneField(staffProfile, on_delete=models.CASCADE, related_name="lab")

    certification = models.CharField(max_length=100)
    lab_type = models.CharField(
        max_length=100,
        help_text="Blood, Pathology, Radiology, Microbiology, etc."
    )




def generate_number(*args, **kwargs):
    return str(uuid.uuid4()).split('-')[0].upper()


class Apointment(models.Model):
    appointment_number = models.CharField(max_length=50,unique=True,default=generate_number)
    schedule = models.DateTimeField()
    remarks = models.CharField(max_length=50)
    doctor = models.ForeignKey(DoctorProfile,related_name='appointment',on_delete=models.CASCADE)
    patient = models.ForeignKey(patientProfile,related_name='patient',on_delete=models.CASCADE)