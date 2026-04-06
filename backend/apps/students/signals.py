from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, DigitalTwin

User = get_user_model()


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Create StudentProfile and DigitalTwin when a new user is created"""
    if created and instance.role == 'student':
        profile = StudentProfile.objects.create(user=instance)
        DigitalTwin.objects.create(student=profile)


@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    """Save StudentProfile when user is saved"""
    if hasattr(instance, 'student_profile'):
        instance.student_profile.save()
