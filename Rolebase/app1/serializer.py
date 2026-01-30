from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group, Permission


from rest_framework import serializers

class RegisterSeriliazer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    admin_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "admin_code"]
    
    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            role="admin"
        )
        AdminProfile.objects.create(user=user, admin_code=validated_data["admin_code"])
        return user


class UserSeriliazer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields=['id','username','email','role']

    def to_representation(self, instance):
        data=super().to_representation(instance)
        if instance.role == "admin":
            data['profile'] =AdminProfile.objects.filter(user=instance).values().first()
        
        elif instance.role == "patient":
            data['profile'] =patientProfile.objects.filter(user=instance).values().first()

        elif instance.role == "staff":
            staff = staffProfile.objects.filter(user=instance).first()
            if staff:
                staff_data = {
                    "id": staff.id,
                    "employee_id": staff.employee_id,
                    "department": staff.department,
                }

                if hasattr(staff, "doctor"):
                    staff_data["doctor"] = {
                        "specialization": staff.doctor.specialization,
                        "license_number": staff.doctor.license_number,
                        "hospital_name": staff.doctor.hospital_name,
                    }
                elif hasattr(staff, "nurse"):
                    staff_data["nurse"] = {
                        "ward": staff.nurse.ward,
                        "license_number": staff.nurse.license_number,
                        "shift": staff.nurse.shift,
                    }
                elif hasattr(staff, "lab"):
                    staff_data["lab"] = {
                        "ward": staff.lab.ward,
                        "lab_type": staff.lab.lab_type,
                    }
                elif hasattr(staff, "accountant"):
                    staff_data["accountant"] = {
                        "certification": staff.accountant.certification,
                        "years_of_experience": staff.accountant.years_of_experience
                    }


                data["profile"] = staff_data
            else:
                data["profile"] = None

        return data

class LoginSerializer(serializers.Serializer): 
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class StaffSerializer(serializers.Serializer):
    password=serializers.CharField(write_only=True)
    username=serializers.CharField()
    employee_id=serializers.CharField()
    department=serializers.CharField()
    staff_type = serializers.ChoiceField(choices=staffProfile.STAFF_TYPE_CHOICES,error_messages={
            "required": "Please select a staff_type from: doctor, nurse, lab, accountant",
            "invalid_choice": "Invalid staff_type. Choose one of: doctor, nurse, lab, accountant"
        })
    # Doctor fields
    specialization = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)
    hospital_name = serializers.CharField(required=False, allow_blank=True)

    accounting_certification=serializers.CharField(required=False,allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False, default=0, min_value=0)
    ward=serializers.CharField(required=False,allow_blank=False)
    shift =serializers.ChoiceField(choices=NurseProfile.Nurse_choices,required=False)
    certification=serializers.CharField(required=False)
    lab_type=serializers.CharField(required=False,allow_blank=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose another one."
            )
        return value



    def validate(self, data):
        staff_type = data.get('staff_type')
        if staff_type == "doctor":
            doctor_fields = ["specialization", "license_number", "hospital_name"]
            missing = [f for f in doctor_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {f: f"{f} is required for doctors" for f in missing}
                )
        if staff_type == "nurse":
            nurse_fields = ["ward", "license_number","shift"]
            missing = [f for f in nurse_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {f: f"{f} is required for doctors" for f in missing}
                )
        if staff_type == "lab":
            lab_fields = ["certification", "lab_type "]
            missing = [f for f in lab_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {f: f"{f} is required for doctors" for f in missing}
                )
        return data
    

    @transaction.atomic
    def create(self, data):
        staff_type = data["staff_type"]
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            role="staff"
        )
        staff = staffProfile.objects.create(
            user=user,
            employee_id=data["employee_id"],
            department=data["department"],
            staff_type=staff_type
        )
        if staff_type == "doctor":
            DoctorProfile.objects.create(
                staff=staff,
                specialization=data["specialization"],
                license_number=data["license_number"],
                hospital_name=data["hospital_name"]
            )
        if staff_type == "accountant":
            AccountantProfile.objects.create(
                staff=staff,
                accounting_certification=data.get("accounting_certification",""),
                years_of_experience=data.get("years_of_experience",0)
            )
        if staff_type == "nurse":
            NurseProfile.objects.create(
                staff=staff,
                license_number=data.get("license_number"),
                years_of_experience=data.get("years_of_experience",0),
                ward=data.get("ward",""),
                shift=data.get("shift")
            )
        if staff_type == "lab":
            LabTechnicianProfile.objects.create(
                staff=staff,
                certification=data.get("certification"),
                lab_type =data.get("lab_type ")
            )
        return user
    
class PatientSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    medical_history = serializers.CharField(required=False, allow_blank=True)
    insurance_number = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            role="patient"
        )
        patientProfile.objects.create(
            user=user,
            medical_history=validated_data.get("medical_history", ""),
            insurance_number=validated_data.get("insurance_number",0)
        )
        return user


class PermissionSeriliazer(serializers.ModelSerializer):
    class Meta:
        model=Permission
        fields = ['id', 'name', 'codename']


class GroupSeriliazer(serializers.ModelSerializer):
    permissions=PermissionSeriliazer(many=True)

    class Meta:
        model=Group
        fields =['id','name','permissions']