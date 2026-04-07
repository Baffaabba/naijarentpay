from django import forms
from .models import Property


class AddPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "title", "property_type", "location", "city", "state",
            "price_per_year", "bedrooms", "bathrooms", "sqft", "age",
            "description", "latitude", "longitude",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ReviewForm(forms.Form):
    RATING_CHOICES = [(i, "★" * i) for i in range(1, 6)]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(),
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Share your experience with this property..."}),
        max_length=1000,
    )
