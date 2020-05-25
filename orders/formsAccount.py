from django.forms import ModelForm
from django import forms
from .models import Account



class AccountForm(ModelForm):

    class Meta:
        model = Account
        fields = ['account_description','account_number']
    
   



   
