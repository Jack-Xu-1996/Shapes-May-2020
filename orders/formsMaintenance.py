from django.forms import ModelForm
from django import forms
from .models import Maintenance


class MaintenanceForm(ModelForm):
	OPTIONS = (('',''),('Foundry','Foundry'),('Extrusion','Extrusion'),('Fabrication','Fabrication'),('Anodizing','Anodizing'))
	department = forms.ChoiceField(choices=OPTIONS)
	class Meta:
		model = Maintenance
		fields = ['date','department','hours','comment']

    
