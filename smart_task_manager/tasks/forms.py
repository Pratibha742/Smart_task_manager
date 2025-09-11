from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task
from django.core.validators import RegexValidator
import re


# 🔥 Default validators ko overwrite karna
User._meta.get_field("username").validators = [
    RegexValidator(
        regex=r'^[A-Za-z0-9 ]+$',
        message="Username may only contain letters, numbers, and spaces."
    )
]

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','due_date','status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date'}),
            'description': forms.Textarea(attrs={'rows':3}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text="Required. Only letters, numbers, and spaces allowed.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


def clean_username(self):
    username = self.cleaned_data["username"].strip()
    return username

