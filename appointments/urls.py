from django.urls import path
from .views import (home,DoctorRegisterView,PatientRegisterView,appointment_list,LoginView,LogoutView,
book_appointment,appointment_list,update_appointment_status,delete_appointment)

urlpatterns = [
    path('', home, name='home'),
    path('doctor_register/', DoctorRegisterView.as_view(), name='doctor_register'),
    path('patient_register/', PatientRegisterView.as_view(), name='patient_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('book_appointment/', book_appointment, name='book_appointment'),
    path('appointment_list/', appointment_list, name='appointment_list'),
    path('update-appointment-status/<int:appointment_id>/', update_appointment_status, name='update_appointment_status'),
    path('delete_appointment/<int:appointment_id>/', delete_appointment, name='delete_appointment'),
]
