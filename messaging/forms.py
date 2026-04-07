from django import forms


class MessageForm(forms.Form):
    content = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Type a message..."}),
        max_length=2000,
    )
