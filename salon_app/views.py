from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta

from .models import User, Service, Employee, TimeSlot, Appointment
from .forms import (
    CustomerRegistrationForm, LoginForm, EmployeeForm, 
    TimeSlotForm, ServiceForm, AppointmentForm
)

#index view
def index(request):
    return render(request, 'index.html')

# Helper functions
def is_admin(user):
    return user.is_authenticated and user.user_type == 'ADMIN'

def is_customer(user):
    return user.is_authenticated and user.user_type == 'CUSTOMER'

# Authentication views
def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to our service.")
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            messages.success(request, f"Welcome back, {user.first_name}!")
            
            if user.user_type == 'ADMIN':
                return redirect('admin_dashboard')
            else:
                return redirect('customer_dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('index')

# Customer views
@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    appointments = Appointment.objects.filter(customer=request.user).order_by('time_slot__date', 'time_slot__start_time')
    upcoming_appointments = appointments.filter(
        Q(status='PENDING') | Q(status='CONFIRMED'),
        time_slot__date__gte=timezone.now().date()
    )
    past_appointments = appointments.filter(
        Q(status='COMPLETED') | Q(status='CANCELLED') |
        (Q(time_slot__date__lt=timezone.now().date()))
    )
    
    return render(request, 'customer/dashboard.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

@login_required
@user_passes_test(is_customer)
def available_slots(request):
    date = request.GET.get('date')
    service_id = request.GET.get('service_id')
    
    # Base queryset for time slots
    slots = TimeSlot.objects.filter(is_available=True)
    
    # Filter by date if provided
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            slots = slots.filter(date=date_obj)
        except ValueError:
            pass
    else:
        # Default to slots from today onwards
        slots = slots.filter(date__gte=timezone.now().date())
    
    # Filter by service if provided
    if service_id:
        try:
            employees = Employee.objects.filter(services__id=service_id)
            slots = slots.filter(employee__in=employees)
        except ValueError:
            pass
    
    # Group slots by date and employee
    grouped_slots = {}
    for slot in slots:
        date_str = slot.date.strftime('%Y-%m-%d')
        
        if date_str not in grouped_slots:
            grouped_slots[date_str] = {}
        
        employee_key = slot.employee.id
        employee_name = f"{slot.employee.user.first_name} {slot.employee.user.last_name}"
        
        if employee_key not in grouped_slots[date_str]:
            grouped_slots[date_str][employee_key] = {
                'name': employee_name,
                'slots': []
            }
        
        grouped_slots[date_str][employee_key]['slots'].append({
            'id': slot.id,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M')
        })
    
    # For AJAX requests, still return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'slots': grouped_slots})
    
    # Get services for filtering
    services = Service.objects.all()
    
    return render(request, 'customer/available_slots.html', {
        'grouped_slots': grouped_slots,
        'services': services,
        'selected_service': service_id,
        'selected_date': date
    })

@login_required
@user_passes_test(is_customer)
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.save()
            
            # Update the time slot availability
            time_slot = appointment.time_slot
            time_slot.is_available = False
            time_slot.save()
            
            messages.success(request, "Appointment booked successfully!")
            return redirect('customer_dashboard')
    else:
        # Pre-fill form with data from query params if available
        initial = {}
        service_id = request.GET.get('service_id')
        time_slot_id = request.GET.get('time_slot_id')
        
        if service_id:
            initial['service'] = service_id
        if time_slot_id:
            initial['time_slot'] = time_slot_id
            # Also set employee based on time slot
            try:
                time_slot = TimeSlot.objects.get(id=time_slot_id)
                initial['employee'] = time_slot.employee.id
            except TimeSlot.DoesNotExist:
                pass
        
        form = AppointmentForm(user=request.user, initial=initial)
    
    # Get available services for form
    services = Service.objects.all()
    
    return render(request, 'customer/book_appointment.html', {
        'form': form,
        'services': services
    })

@login_required
@user_passes_test(is_customer)
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user)
    
    if request.method == 'POST':
        # Only allow cancellation of pending or confirmed appointments
        if appointment.status in ['PENDING', 'CONFIRMED']:
            appointment.status = 'CANCELLED'
            appointment.save()
            
            # Make the time slot available again
            time_slot = appointment.time_slot
            time_slot.is_available = True
            time_slot.save()
            
            messages.success(request, "Appointment cancelled successfully.")
            return redirect('customer_dashboard')
        else:
            messages.error(request, "Cannot cancel this appointment.")
            return redirect('customer_dashboard')
    
    # Confirmation page
    return render(request, 'customer/cancel_appointment.html', {
        'appointment': appointment
    })



# Admin views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='PENDING').count()
    total_customers = User.objects.filter(user_type='CUSTOMER').count()
    total_employees = Employee.objects.count()
    
    # Get today's appointments
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(time_slot__date=today)
    
    return render(request, 'admin/dashboard.html', {
        'stats': {
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'total_customers': total_customers,
            'total_employees': total_employees,
        },
        'today_appointments': today_appointments
    })

@login_required
@user_passes_test(is_admin)
def manage_employees(request):
    employees = Employee.objects.all()
    return render(request, 'admin/manage_employees.html', {
        'employees': employees
    })

@login_required
@user_passes_test(is_admin)
def add_employee(request):
    if request.method == 'POST':
        # Process employee creation
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        bio = request.POST.get('bio')
        service_ids = request.POST.getlist('services')
        
        try:
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                user_type='EMPLOYEE'
            )
            
            # Create employee profile
            employee = Employee.objects.create(user=user, bio=bio)
            
            # Add services
            if service_ids:
                services = Service.objects.filter(id__in=service_ids)
                employee.services.set(services)
            
            messages.success(request, f"Employee {first_name} {last_name} created successfully.")
            return redirect('manage_employees')
        except Exception as e:
            messages.error(request, f"Error creating employee: {str(e)}")
    
    # Get services for form
    services = Service.objects.all()
    
    return render(request, 'admin/add_employee.html', {
        'services': services
    })

@login_required
@user_passes_test(is_admin)
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        # Update employee
        user = employee.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        
        # Update password if provided
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        
        # Update employee profile
        employee.bio = request.POST.get('bio', employee.bio)
        employee.save()
        
        # Update services
        service_ids = request.POST.getlist('services')
        if service_ids:
            services = Service.objects.filter(id__in=service_ids)
            employee.services.set(services)
        
        messages.success(request, f"Employee {user.first_name} {user.last_name} updated successfully.")
        return redirect('manage_employees')
    
    # Get services for form
    services = Service.objects.all()
    
    return render(request, 'admin/edit_employee.html', {
        'employee': employee,
        'services': services,
        'selected_services': employee.services.all()
    })

@login_required
@user_passes_test(is_admin)
def manage_services(request):
    services = Service.objects.all()
    return render(request, 'admin/manage_services.html', {
        'services': services
    })

@login_required
@user_passes_test(is_admin)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"Service '{service.name}' created successfully.")
            return redirect('manage_services')
    else:
        form = ServiceForm()
    
    return render(request, 'admin/add_service.html', {
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service '{service.name}' updated successfully.")
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'admin/edit_service.html', {
        'form': form,
        'service': service
    })

@login_required
@user_passes_test(is_admin)
def manage_time_slots(request):
    employees = Employee.objects.all()
    
    return render(request, 'admin/manage_time_slots.html', {
        'employees': employees
    })

@login_required
@user_passes_test(is_admin)
def add_time_slot(request):
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save()
            messages.success(request, "Time slot added successfully.")
            return redirect('manage_time_slots')
    else:
        form = TimeSlotForm()
    
    # Get employees for form
    employees = Employee.objects.all()
    
    return render(request, 'admin/add_time_slot.html', {
        'form': form,
        'employees': employees
    })

@login_required
@user_passes_test(is_admin)
def manage_appointments(request):
    # Get filter parameters
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    appointments = Appointment.objects.all().order_by('time_slot__date', 'time_slot__start_time')
    
    # Apply filters
    if status:
        appointments = appointments.filter(status=status)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            appointments = appointments.filter(time_slot__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            appointments = appointments.filter(time_slot__date__lte=date_to_obj)
        except ValueError:
            pass
    
    return render(request, 'admin/manage_appointments.html', {
        'appointments': appointments,
        'status_choices': Appointment.STATUS_CHOICES,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to
    })

@login_required
@user_passes_test(is_admin)
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        
        if status in [s[0] for s in Appointment.STATUS_CHOICES]:
            old_status = appointment.status
            appointment.status = status
            appointment.save()
            
            # If appointment was canceled, make the time slot available again
            if status == 'CANCELLED' and old_status != 'CANCELLED':
                appointment.time_slot.is_available = True
                appointment.time_slot.save()
            
            messages.success(request, f"Appointment status updated to {dict(Appointment.STATUS_CHOICES)[status]}.")
            return redirect('manage_appointments')
        else:
            messages.error(request, "Invalid status selected.")
    
    return render(request, 'admin/update_appointment_status.html', {
        'appointment': appointment,
        'status_choices': Appointment.STATUS_CHOICES
    })



# feedback views
from django.views.generic import CreateView,FormView,ListView,UpdateView
from django.urls import reverse_lazy
from .forms import AddFeedback
from .models import Feedbacks

from django.contrib.auth.mixins import LoginRequiredMixin

class AddfeedbackView(LoginRequiredMixin, CreateView):
    template_name = "feedback/feedback.html"
    form_class = AddFeedback
    model = Feedbacks
    success_url = reverse_lazy("customer_dashboard")
    login_url = 'login'  # Replace with your login URL name
    
    def form_valid(self, form):
        # Set the customer to the currently logged-in user
        form.instance.customer = self.request.user
        return super().form_valid(form)

class FeedbacksView(ListView):
    template_name="admin/feedbacks.html"
    model=Feedbacks
    context_object_name="feedbacks"  
