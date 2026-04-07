from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Email or username", "class": "w-full"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "w-full"})
    )


class RegisterStep1Form(forms.Form):
    ROLE_CHOICES = [("tenant", "Tenant"), ("landlord", "Landlord")]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.HiddenInput())
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    id_document = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        cpw = cleaned_data.get("confirm_password")
        if pw and cpw and pw != cpw:
            raise forms.ValidationError("Passwords do not match.")
        email = cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return cleaned_data


class RegisterStep2Form(forms.Form):
    otp = forms.CharField(max_length=6, label="Verification Code")
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=255, required=False)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "address", "avatar"]


class SecurityForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_new_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") != cleaned.get("confirm_new_password"):
            raise forms.ValidationError("New passwords do not match.")
        return cleaned
