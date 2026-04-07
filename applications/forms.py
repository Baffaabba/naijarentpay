from django import forms


EMPLOYMENT_CHOICES = [
    ("", "Select employment status"),
    ("employed", "Employed"),
    ("self_employed", "Self-Employed"),
    ("business_owner", "Business Owner"),
    ("student", "Student"),
    ("other", "Other"),
]


class ApplicationForm(forms.Form):
    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "w-full"}),
    )
    monthly_income = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Monthly income in ₦ (optional)"}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Introduce yourself to the landlord..."}),
        required=False,
    )
