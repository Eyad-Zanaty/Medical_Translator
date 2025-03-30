from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model for healthcare translation app"""
    email = models.EmailField(unique=True)
    organization = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50, blank=True)
    is_healthcare_provider = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
