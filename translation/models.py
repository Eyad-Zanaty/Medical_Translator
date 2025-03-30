from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):
    """Custom user model for healthcare translation app"""
    organization = models.CharField(max_length=100, blank=True)
    is_healthcare_provider = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

class Translation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='translations', null=True)
    original_text = models.TextField()
    translated_text = models.TextField()
    source_language = models.CharField(max_length=5)
    target_language = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    medical_terms = models.JSONField(default=dict, blank=True)
    is_favorite = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['source_language', 'target_language']),
        ]

    def __str__(self):
        return f"{self.source_language} to {self.target_language} - {self.original_text[:50]}..."