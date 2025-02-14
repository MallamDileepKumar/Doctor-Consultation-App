from django.db import models
from django.contrib.auth.hashers import make_password

class Doctor_Register(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, null=False, blank=False)
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()
    phone = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name 


class Patient_Register(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, null=False, blank=False)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    gmail = models.EmailField()

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    doctor = models.ForeignKey(Doctor_Register, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient_Register, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    meeting_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Appointment {self.doctor.full_name} with {self.patient.full_name} on {self.date_time}"
