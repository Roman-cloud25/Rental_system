"""
User model
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


# User manager used instead of username
class UserManager(BaseUserManager):
    # Creating a standard user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')

        # Email address to lowercase
        email = self.normalize_email(email)

        # Create a user without saving to the database
        user = self.model(email=email, **extra_fields)

        # Hashing the password
        user.set_password(password)

        # Save a user to the database
        user.save(using=self._db)
        return user

    # Creating administrator
    def create_superuser(self, email, password=None, **extra_fields):
        # Administrator with all permissions
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Administrator role: admin
        extra_fields.setdefault('role', 'admin')

        # Check permissions
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Administrator must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Administrator must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


# User model
class User(AbstractBaseUser, PermissionsMixin):
    # Role
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('both', 'Tenant and Landlord'),
        ('admin', 'Administrator'),
    ]

    # Main fields
    email = models.EmailField(
        unique=True,
        verbose_name='Email address ',
        help_text='Used to login'
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Full name',
        help_text='What should we call you?'
    )

    # Phone
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Phone number',
        validators=[RegexValidator(r'^\+?[0-9\s\-\(\)]+$', 'Please enter a valid phone number')]
    )

    # Role Tenant
    is_tenant = models.BooleanField(
        default=True,
        verbose_name='Tenant',
        help_text='Can view and accommodations'
    )

    # Role landlord
    is_landlord = models.BooleanField(
        default=False,
        verbose_name='Landlord',
        help_text='Can create and manage ads'
    )

    # Role field
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='tenant',
        verbose_name='Role'
    )

    # System fields Django
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activ',
        help_text='Check if the user should have access'
    )

    # Access to the Django admin panel
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff',
        help_text='Can log into the admin panel'
    )

    # Data of registration
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data of registration'
    )

    # Last login date
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Last login'
    )

    # Authentication settings
    # Login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            # Quick search by Email
            models.Index(fields=['email']),
            # Filtering by roles
            models.Index(fields=['is_tenant', 'is_landlord']),
        ]

    def __str__(self):
        # User display
        return f"{self.name} ({self.email})"

    # User check only tenant
    @property
    def is_tenant_only(self):
        return self.is_tenant and not self.is_landlord

    # User check only landlord
    @property
    def is_landlord_only(self):
        return self.is_landlord and not self.is_tenant

    # User check and tenant and landlord
    @property
    def is_both(self):
        return self.is_tenant and self.is_landlord

    # Updates the role field
    def save(self, *args, **kwargs):
        if self.is_superuser or self.role == 'admin':
            self.role = 'admin'
        elif self.is_tenant and self.is_landlord:
            self.role = 'both'
        elif self.is_landlord:
            self.role = 'landlord'
        else:
            self.role = 'tenant'

        super().save(*args, **kwargs)
