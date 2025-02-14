from django.contrib import admin
from .models import Doctor_Register,Patient_Register,Appointment

# Register your models here.
admin.site.register(Doctor_Register)
admin.site.register(Patient_Register)
admin.site.register(Appointment)
