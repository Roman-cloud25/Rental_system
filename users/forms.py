"""
User forms
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User


# User registration form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label='Email address'
    )

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
        label='Full name'
    )

    # Selecting a role during registration
    role_choice = forms.ChoiceField(
        choices=[
            ('tenant', 'I want to rent a place to live'),
            ('landlord', 'I want to rent out a property'),
            ('both', 'I want to both rent and rent out a place to live'),
        ],
        widget=forms.RadioSelect,
        label='Select status',
        initial='tenant'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password'
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label='Confirm password'
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'role_choice', 'password1', 'password2')

    # Verification Email must not already be registered
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Sorry, a user with this Email is already registered')
        return email

    # Saving the user with the correct roles
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']

        # Roles based on user choice
        role = self.cleaned_data['role_choice']
        if role == 'tenant':
            user.is_tenant = True
            user.is_landlord = False
        elif role == 'landlord':
            user.is_tenant = False
            user.is_landlord = True
        else:  # both
            user.is_tenant = True
            user.is_landlord = True

        if commit:
            user.save()
        return user


# Login form
class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label='Email'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password'
    )

    # Email and password authentication
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Invalid Email or password')
            if not user.is_active:
                raise forms.ValidationError('Accound not activated. Please check your Email')
            self.cleaned_data['user'] = user
        return self.cleaned_data

    # Authenticated user returned
    def get_user(self):
        return self.cleaned_data.get('user')


# Profile edit form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'phone_number', 'is_landlord')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_landlord': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_landlord'].label = 'I want to rent out my property'
