from rest_framework import serializers
from .models import User, Service, Employee, TimeSlot, Appointment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'address', 'user_type']
        read_only_fields = ['user_type']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'user', 'bio', 'services']

class TimeSlotSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'employee', 'employee_name', 'date', 'start_time', 'end_time', 'is_available']
        read_only_fields = ['is_available']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}"

class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'customer_name', 'employee', 'employee_name', 
            'service', 'service_name', 'time_slot', 'appointment_date', 
            'appointment_time', 'status', 'notes', 'created_at'
        ]
        read_only_fields = ['customer', 'created_at']
    
    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}"
    
    def get_service_name(self, obj):
        return obj.service.name
    
    def get_appointment_date(self, obj):
        return obj.time_slot.date
    
    def get_appointment_time(self, obj):
        return obj.time_slot.start_time
