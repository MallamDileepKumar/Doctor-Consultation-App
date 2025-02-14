import json  # ✅ Ensure this is at the top
import random
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # For handling CSRF on AJAX
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Doctor_Register, Patient_Register, Appointment
from django.core.mail import EmailMessage





# Helper function to generate meeting link
def generate_meeting_link():
    meeting_code = "https://meet.google.com/qbq-bthq-net"
    return meeting_code

# Helper function for registration logic
def register_user(user_type, request):
    if user_type == 'doctor':
        user_model = Doctor_Register
        redirect_url = 'appointment_list'
    else:
        user_model = Patient_Register
        redirect_url = 'book_appointment'

    username = request.POST.get('username')
    if user_model.objects.filter(username=username).exists():
        messages.error(request, f'{user_type.capitalize()} username already exists. Please choose another one.')
        return redirect(f'{user_type}_register')

    user = user_model(
        username=username,
        password=request.POST.get('password'),
        full_name=request.POST.get('full_name'),
        phone=request.POST.get('phone'),
        **{field: request.POST.get(field) for field in ['specialization', 'experience', 'age', 'gender', 'gmail'] if field in request.POST}
    )
    user.save()
    messages.success(request, f'{user_type.capitalize()} registered successfully.')
    return redirect(redirect_url)

# Home Page
def home(request):
    if 'user_type' in request.session:
        if request.session['user_type'] == 'doctor':
            return redirect('appointment_list')
        elif request.session['user_type'] == 'patient':
            return redirect('book_appointment')
    return render(request, 'appointments/home.html')

# Doctor Registration
class DoctorRegisterView(View):
    def get(self, request):
        return render(request, 'appointments/doctor_register.html')

    def post(self, request):
        return register_user('doctor', request)

# Patient Registration
class PatientRegisterView(View):
    def get(self, request):
        return render(request, 'appointments/patient_register.html')

    def post(self, request):
        return register_user('patient', request)

# Login
class LoginView(View):
    def get(self, request):
        return render(request, 'appointments/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        doctor = Doctor_Register.objects.filter(username=username).first()
        if doctor and check_password(password, doctor.password):
            request.session['user_type'] = 'doctor'
            request.session['user_id'] = doctor.id
            messages.success(request, 'Logged in as Doctor.')
            return redirect('appointment_list')

        patient = Patient_Register.objects.filter(username=username).first()
        if patient and check_password(password, patient.password):
            request.session['user_type'] = 'patient'
            request.session['user_id'] = patient.id
            messages.success(request, 'Logged in as Patient.')
            return redirect('book_appointment')

        messages.error(request, 'Invalid username or password.')
        return redirect('login')

# Logout
class LogoutView(View):
    def get(self, request):
        del request.session['user_type']
        del request.session['user_id']
        messages.success(request, 'Logged out successfully.')
        return redirect('home')

# Book Appointment
def book_appointment(request):
    if request.session.get('user_type') != 'patient':
        messages.error(request, 'You must be logged in as a patient to book an appointment.')
        return redirect('login')

    patient = get_object_or_404(Patient_Register, id=request.session.get('user_id'))
    if request.method == 'POST':
        doctor = get_object_or_404(Doctor_Register, id=request.POST.get('doctor'))
        appointment = Appointment(doctor=doctor, patient=patient, date_time=request.POST.get('date_time'))
        appointment.save()
        messages.success(request, 'Appointment booked successfully')
        return redirect('appointment_list')

    return render(request, 'appointments/book_appointment.html', {'doctors': Doctor_Register.objects.all(), 'patient': patient})

# Appointment List
def appointment_list(request):
    if 'user_type' not in request.session:
        messages.error(request, 'You must be logged in to view appointments.')
        return redirect('login')

    user_type, user_id = request.session.get('user_type'), request.session.get('user_id')
    appointments = Appointment.objects.filter(doctor_id=user_id) if user_type == 'doctor' else Appointment.objects.filter(patient_id=user_id)
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

# Update Appointment Status with WebSockets Notification

# Optimized function to handle appointment confirmation and meeting link generation
@csrf_exempt
def update_appointment_status(request, appointment_id):
    if request.method == "POST":
        # Fetch the appointment object
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Parse the incoming JSON data
        try:
            data = json.loads(request.body)
            new_status = data.get("status")

            if not new_status:
                return JsonResponse({"error": "Status is required."}, status=400)

            # Update the appointment status
            appointment.status = new_status
            appointment.save()

            # Default: No meeting link
            meeting_link = None

            # If the status is "Confirmed", generate and send the meeting link
            if new_status == "Confirmed":
                meeting_link = generate_meeting_link()  # Dynamically generate the link
                appointment.meeting_link = meeting_link
                appointment.save()

                # Send email notification to the patient for confirmed status with the meeting link
                send_appointment_confirmation_email(appointment)

            # Send email notification to the patient for other status updates (without meeting link)
            elif new_status != "Confirmed":
                send_appointment_status_update_email(appointment)

            return JsonResponse({
                "message": "Appointment updated successfully.",
                "status": new_status,
                "meeting_link": meeting_link,  # May be None if not confirmed
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    # In case of non-POST request
    return JsonResponse({"error": "Invalid request method."}, status=400)


# Send email notification to the patient when the status is "Confirmed"
def send_appointment_confirmation_email(appointment):
    patient_email = appointment.patient.gmail  # Assuming the patient's email is stored in the `gmail` field
    doctor_name = appointment.doctor.full_name
    appointment_time = appointment.date_time
    meeting_link = appointment.meeting_link  # This will be generated when the status is "Confirmed"

    subject = "Your Appointment Confirmation"
    message = f"""
    <html>
    <body>
        <p>Hello {appointment.patient.full_name},</p>
        <p>Your appointment with Dr. {doctor_name} has been confirmed.</p>
        <p><strong>Appointment Details:</strong></p>
        <ul>
            <li><strong>Date and Time:</strong> {appointment_time}</li>
            <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
        </ul>
        <p>To join your video consultation, click the link below:</p>
        <p><a href="{meeting_link}" target="_blank">{meeting_link}</a></p>
        <p>If you have any questions, feel free to contact us.</p>
        <p>Best regards,<br>The Appointment Team</p>
    </body>
    </html>
    """
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [patient_email])
    email.content_subtype = "html"  # Set content type to HTML
    email.send(fail_silently=False)

def send_appointment_status_update_email(appointment):
    """
    Sends an email to the patient when their appointment status is updated to 'Pending' or 'Completed'.
    """
    # Check if status is "Pending" or "Completed" before sending email
    if appointment.status in ["Pending", "Completed"]:
        patient_email = appointment.patient.gmail  # Ensure field name is correct
        doctor_name = appointment.doctor.full_name
        appointment_time = appointment.date_time.strftime("%Y-%m-%d %H:%M")  # Format date & time

        subject = "Your Appointment Status Update"
        message = f"""
        <html>
        <body>
            <p>Hello {appointment.patient.full_name},</p>
            <p>Your appointment with Dr. {doctor_name} has been <strong>{appointment.status}</strong>.</p>
            <p><strong>Appointment Details:</strong></p>
            <ul>
                <li><strong>Date and Time:</strong> {appointment_time}</li>
                <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
            </ul>
            <p>If you have any questions, feel free to contact us.</p>
            <p>Best regards,<br>The Appointment Team</p>
        </body>
        </html>
        """
        email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [patient_email])
        email.content_subtype = "html"  # Ensure email is sent as HTML
        email.send(fail_silently=False)  # Change to True in production to avoid errors stopping execution 


# Delete Appointment
def delete_appointment(request, appointment_id):
    if 'user_type' not in request.session:
        messages.error(request, 'You must be logged in to delete an appointment.')
        return redirect('login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.session['user_type'] == 'patient' and appointment.patient.id == request.session['user_id']:
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
    else:
        messages.error(request, 'Unauthorized action.')
    
    return redirect('appointment_list')
