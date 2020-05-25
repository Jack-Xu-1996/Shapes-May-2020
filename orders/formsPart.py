from django.forms import ModelForm
from django import forms
from .models import Part



class PartForm(ModelForm):

    class Meta:
        model = Part
        fields = ['part_description','part_number']
    
   



   
