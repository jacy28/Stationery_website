from django import forms
from .models import ContactMessage, BillingDetails

class ContactForm(forms.ModelForm):
    class Meta:
        model=ContactMessage
        fields=["name", "email", "phone", "message"]
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control rounded-4 p-3 input-blue', 'placeholder':'Enter your name'}),
            'email':forms.EmailInput(attrs={'class':'form-control rounded-4 p-3 input-blue', 'placeholder':'Enter your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control rounded-4 p-3 input-blue', 'placeholder': 'Enter your number'}),
            'message': forms.Textarea(attrs={'class': 'form-control rounded-4 p-3 input-blue', 'rows': 2, 'placeholder': 'Enter Message'}),
        }

class BillingForm(forms.ModelForm):
    class Meta:
        model=BillingDetails
        fields=["name", "address", "city", "code"]
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control rounded-4 p-3 input-blue', 'placeholder':'Enter your name'}),
            'address':forms.Textarea(attrs={'class':'form-control rounded-4 p-3 input-blue', 'rows': 2, 'placeholder':'Enter your address'}),
            'city': forms.TextInput(attrs={'class': 'form-control rounded-4 p-3 input-blue', 'placeholder': 'Enter your City'}),
            'code': forms.TextInput(attrs={'class': 'form-control rounded-4 p-3 input-blue', 'placeholder':'Enter your postal code'}),
        }




