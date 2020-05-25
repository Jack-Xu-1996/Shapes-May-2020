from django.forms import ModelForm
from django import forms
from .models import Revenue


class RevenueForm(ModelForm):
    
    class Meta:
        model = Revenue 
        fields = ['date','revenue']

