from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'role',
            'institute',
            'class_studying',
            'stream',
            'password1',
            'password2',
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        cls = cleaned_data.get("class_studying")
        stream = cleaned_data.get("stream")

        if role == "STUDENT":
            if cls in [11, 12] and not stream:
                raise forms.ValidationError("Stream required for class 11 & 12")
        return cleaned_data
