from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task
import re

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
        help_text="Required. 150 characters or fewer. Letters, numbers, spaces and ./-/_ allowed.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if username:
            username = username.strip().replace(" ","_")
        if not re.match(r'^[A-Za-z0-9 _\.\-]+$', username):
            raise forms.ValidationError(
                "Username may only contain letters, numbers, spaces, and ./-/_ characters."
            )
        return username
