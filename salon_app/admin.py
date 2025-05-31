from django.contrib import admin
from .models import User, Service, Employee, TimeSlot, Appointment

# Register models for admin interface
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'get_employee_email')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('services',)
    
    def get_employee_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_employee_name.short_description = 'Name'
    
    def get_employee_email(self, obj):
        return obj.user.email
    get_employee_email.short_description = 'Email'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available')
    ordering = ('date', 'start_time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'employee', 'get_appointment_date', 'get_appointment_time', 'status')
    list_filter = ('status', 'time_slot__date')
    search_fields = ('customer__email', 'employee__user__email', 'service__name')
    ordering = ('time_slot__date', 'time_slot__start_time')
    
    def get_appointment_date(self, obj):
        return obj.time_slot.date
    get_appointment_date.short_description = 'Date'
    
    def get_appointment_time(self, obj):
        return obj.time_slot.start_time
    get_appointment_time.short_description = 'Time'
