from django import forms
from .models import Laptop
from .models import Owner

from django.contrib.auth.models import User

class LaptopForm(forms.ModelForm):


    class Meta:
        model = Laptop
        fields = ('laptop_name', 'laptop_model', 'serial_number', 'laptop_color',)


class OwnerForm(forms.ModelForm):


    class Meta:
        model = Owner
        fields = ('owner_first_name', 'owner_last_name', 'department', 'owner_id','phone_number','image','owner_type',)



class UserLoginForm(forms.Form):
    username = forms.CharField(label="")
    password = forms.CharField(label="",widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput(attrs = {'placeholder' : 'Enter password here..'}))
    confirm_password = forms.CharField(widget = forms.PasswordInput(attrs = {'placeholder' : 'Confirm password'}))
    class Meta:
        model = User
        fields = {
            'username',
            'first_name',
            'last_name',
            'email',
        }

def clean_confirm_password(self):
    password = self.cleaned_data.get('password')
    confirm_password = self.cleaned_data.get('confirm_password')
    if password != confirm_password:
        raise forms.ValidationError("Password Mismatch")
    return confirm_password
