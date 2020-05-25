from django.forms import ModelForm
from django import forms
from .models import Capitalinjection


class CapitalinjectionForm(ModelForm):
    
    class Meta:
        model = Capitalinjection
        fields = ['date','capital_injection_amount','capital_injection_comment']
