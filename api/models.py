from django.db import models

class CustomUser(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('teacher', 'Teacher'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    is_profile_created = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.role}"


class Otp(models.Model):
    email = models.EmailField()
    otp_type = models.CharField(max_length=50)  # e.g., 'email_verification', 'mobile_verification', 'password_reset'
    otp=models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"OTP for {self.email} - Type: {self.otp_type}"