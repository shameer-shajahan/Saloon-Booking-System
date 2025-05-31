from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Service, Employee, TimeSlot, Appointment

User = get_user_model()

class SalonAppTests(TestCase):
    def setUp(self):
        # Create test admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            user_type='ADMIN'
        )
        
        # Create test customer user
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='customerpassword',
            first_name='Customer',
            last_name='User',
            phone='1234567890',
            user_type='CUSTOMER'
        )
        
        # Create test employee user
        self.employee_user = User.objects.create_user(
            email='employee@example.com',
            password='employeepassword',
            first_name='Employee',
            last_name='User',
            user_type='EMPLOYEE'
        )
        
        # Create test service
        self.service = Service.objects.create(
            name='Haircut',
            description='Standard haircut service',
            price=25.00,
            duration=30
        )
        
        # Create employee profile
        self.employee = Employee.objects.create(
            user=self.employee_user,
            bio='Professional hairstylist'
        )
        self.employee.services.add(self.service)
        
        # Create time slots
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        self.time_slot1 = TimeSlot.objects.create(
            employee=self.employee,
            date=tomorrow,
            start_time='10:00',
            end_time='10:30',
            is_available=True
        )
        
        self.time_slot2 = TimeSlot.objects.create(
            employee=self.employee,
            date=tomorrow,
            start_time='11:00',
            end_time='11:30',
            is_available=True
        )
        
        # Set up the test client
        self.client = Client()
    
    def test_customer_registration(self):
        # Test customer registration
        data = {
            'email': 'newcustomer@example.com',
            'password1': 'newcustomerpassword',
            'password2': 'newcustomerpassword',
            'first_name': 'New',
            'last_name': 'Customer',
            'phone': '0987654321'
        }
        
        response = self.client.post(reverse('register'), data)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(email='newcustomer@example.com').exists())
        
        # Check if user type is customer
        new_user = User.objects.get(email='newcustomer@example.com')
        self.assertEqual(new_user.user_type, 'CUSTOMER')
    
    def test_customer_login(self):
        # Test customer login
        response = self.client.post(reverse('login'), {
            'username': 'customer@example.com',
            'password': 'customerpassword'
        })
        
        # Check if login is successful
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_book_appointment(self):
        # Log in as customer
        self.client.login(username='customer@example.com', password='customerpassword')
        
        # Book an appointment
        data = {
            'service': self.service.id,
            'employee': self.employee.id,
            'time_slot': self.time_slot1.id,
            'notes': 'Test appointment'
        }
        
        response = self.client.post(reverse('book_appointment'), data)
        
        # Check if appointment was created
        self.assertEqual(Appointment.objects.count(), 1)
        
        # Check if time slot is now unavailable
        self.time_slot1.refresh_from_db()
        self.assertFalse(self.time_slot1.is_available)
    
    def test_cancel_appointment(self):
        # Log in as customer
        self.client.login(username='customer@example.com', password='customerpassword')
        
        # Create an appointment
        appointment = Appointment.objects.create(
            customer=self.customer_user,
            employee=self.employee,
            service=self.service,
            time_slot=self.time_slot1,
            status='CONFIRMED'
        )
        
        # Cancel the appointment
        response = self.client.post(reverse('cancel_appointment', args=[appointment.id]))
        
        # Check if appointment status is updated
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'CANCELLED')
        
        # Check if time slot is available again
        self.time_slot1.refresh_from_db()
        self.assertTrue(self.time_slot1.is_available)
    
    def test_admin_create_service(self):
        # Log in as admin
        self.client.login(username='admin@example.com', password='adminpassword')
        
        # Create a new service
        data = {
            'name': 'Manicure',
            'description': 'Nail care service',
            'price': 15.00,
            'duration': 45
        }
        
        response = self.client.post(reverse('add_service'), data)
        
        # Check if service was created
        self.assertTrue(Service.objects.filter(name='Manicure').exists())
    
    def test_admin_create_time_slot(self):
        # Log in as admin
        self.client.login(username='admin@example.com', password='adminpassword')
        
        # Create a new time slot
        tomorrow = timezone.now().date() + timedelta(days=1)
        data = {
            'employee': self.employee.id,
            'date': tomorrow,
            'start_time': '14:00',
            'end_time': '14:30'
        }
        
        response = self.client.post(reverse('add_time_slot'), data)
        
        # Check if time slot was created
        self.assertTrue(TimeSlot.objects.filter(start_time='14:00').exists())
