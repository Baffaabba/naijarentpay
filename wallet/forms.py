from django import forms


QUICK_AMOUNTS = [500, 1000, 2000, 5000, 10000, 20000]


class QuickSaveForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1)
    goal_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)


class FundWalletStep1Form(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=100)


class FundWalletStep2Form(forms.Form):
    METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("card", "Debit / Credit Card"),
        ("ussd", "USSD"),
    ]
    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.RadioSelect())
