from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import User

USER_TYPE = (
    (0,'Administrator'),
    (1,'Seller'),
    (2,'Customer')
)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    cpass = forms.CharField(label='Repeat password',widget=forms.PasswordInput)

    date_registered = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    user_type = forms.ChoiceField(choices=USER_TYPE)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        cpass = cleaned_data.get('cpass')
        if password != cpass:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ContactForm(forms.ModelForm):
    name = forms.CharField(label='Your name', max_length=100)
    email = forms.EmailField(label='Your email')
    subject = forms.CharField(label='Subject', max_length=100)
    message = forms.CharField(label='Your message', widget=forms.Textarea)




