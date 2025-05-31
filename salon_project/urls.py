"""
URL configuration for salon_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from salon_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('salon_app.urls')),


    #index path
    path('', views.index, name='index'),


        # Admin URLs
    path('copy@IHRD_PROJECT/dashboard/', views.admin_dashboard, name='admin_dashboard'),

        # Employee management
    path('employees/', views.manage_employees, name='manage_employees'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    
    # Service management
    path('services/', views.manage_services, name='manage_services'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    
    # Time slot management
    path('time-slots/', views.manage_time_slots, name='manage_time_slots'),
    path('time-slots/add/', views.add_time_slot, name='add_time_slot'),
    
    # Appointment management
    path('appointments/', views.manage_appointments, name='manage_appointments'),
    path('appointments/update-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),



]