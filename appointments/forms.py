form django.forms import ModelForm
from .models import Doctor_Register, Patient_Register, Appointment

class Doctor_RegisterForm(ModelForm):
    class Meta:
        model = Doctor_Register
        fields = ['name', 'specialization', 'experience', 'phone']