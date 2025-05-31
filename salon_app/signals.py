from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Appointment, User, TimeSlot

@receiver(post_save, sender=Appointment)
def update_time_slot_availability(sender, instance, created, **kwargs):
    """
    Signal to update time slot availability when an appointment is created or updated
    """
    if created:
        # When a new appointment is created, mark the time slot as unavailable
        time_slot = instance.time_slot
        time_slot.is_available = False
        time_slot.save()
    else:
        # If an appointment is updated to CANCELLED, make the slot available again
        if instance.status == 'CANCELLED':
            time_slot = instance.time_slot
            time_slot.is_available = True
            time_slot.save()
        # If an appointment is changed from CANCELLED to something else, make the slot unavailable
        elif instance.status != 'CANCELLED':
            time_slot = instance.time_slot
            time_slot.is_available = False
            time_slot.save()

# You can add more signals if needed, such as:
# - Sending email notifications when an appointment is created/updated
# - Automatic status updates based on time
# - Cleaning up old/expired time slots
