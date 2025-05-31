from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_customer, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Customer URLs
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/available-slots/', views.available_slots, name='available_slots'),
    path('customer/book-appointment/', views.book_appointment, name='book_appointment'),
    path('customer/cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    
    # Admin URLs
    # path('salon-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),    

    # Employee management
    path('admin/employees/', views.manage_employees, name='manage_employees'),
    path('admin/employees/add/', views.add_employee, name='add_employee'),
    path('admin/employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    
    # Service management
    path('admin/services/', views.manage_services, name='manage_services'),
    path('admin/services/add/', views.add_service, name='add_service'),
    path('admin/services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    
    # Time slot management
    path('admin/time-slots/', views.manage_time_slots, name='manage_time_slots'),
    path('admin/time-slots/add/', views.add_time_slot, name='add_time_slot'),
    
    # Appointment management
    path('admin/appointments/', views.manage_appointments, name='manage_appointments'),
    path('admin/appointments/update-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),

# feedbacl urls 
    path("feedbacks/",views.FeedbacksView.as_view(),name="feedbacks"),
    path("feedback/add/",views.AddfeedbackView.as_view(),name="feedback-add"),


]
