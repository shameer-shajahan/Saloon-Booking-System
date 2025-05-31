from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Appointment, Service, Employee, TimeSlot

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'phone', 'address', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'CUSTOMER'
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    
    class Meta:
        model = User
        fields = ['username', 'password']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['bio', 'services']
        widgets = {
            'services': forms.CheckboxSelectMultiple(),
        }

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time', 'end_time', 'employee']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'employee', 'time_slot', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        available_only = kwargs.pop('available_only', True)
        super().__init__(*args, **kwargs)
        
        # If this is for a customer, only show available time slots
        if user and user.user_type == 'CUSTOMER' and available_only:
            self.fields['time_slot'].queryset = TimeSlot.objects.filter(is_available=True)
            
        # When an employee is selected, filter time slots for that employee
        if 'employee' in self.data:
            try:
                employee_id = int(self.data.get('employee'))
                self.fields['time_slot'].queryset = TimeSlot.objects.filter(
                    employee_id=employee_id, 
                    is_available=True if available_only else True
                )
            except (ValueError, TypeError):
                pass

from .models import Feedbacks
class AddFeedback(forms.ModelForm):

    class Meta:
        model = Feedbacks
        fields = ["rating", "comment"]
        widgets = {
                        
            'rating': forms.NumberInput(attrs={'class': 'form-control'}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

