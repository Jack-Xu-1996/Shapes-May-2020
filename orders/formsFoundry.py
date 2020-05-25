from django.forms import ModelForm
from django import forms
from .models import *
from django.utils.timezone import datetime


class FoundryForm(ModelForm):

    OPTIONS = (
        ('',''),
        ('High','H'),
        ('Low','L'),
    )
    """
    OPTIONS2 = (
        ('Process', 'Process'),
        ('Complete', 'Complete'),
    )
    """

    Mg_HL = forms.ChoiceField(choices=OPTIONS)
    Si_HL = forms.ChoiceField(choices=OPTIONS)
    Fe_HL = forms.ChoiceField(choices=OPTIONS)
    Cu_HL = forms.ChoiceField(choices=OPTIONS)
    Cr_HL = forms.ChoiceField(choices=OPTIONS)
    Mn_HL = forms.ChoiceField(choices=OPTIONS)
    Zn_HL = forms.ChoiceField(choices=OPTIONS)
    Ti_HL = forms.ChoiceField(choices=OPTIONS)
    Bo_HL = forms.ChoiceField(choices=OPTIONS)
    #process_status = forms.TypedChoiceField(required=False, choices=OPTIONS2, widget=forms.RadioSelect)

    class Meta:
        model = Foundry
        fields = ['date','furnace_number','heat_number','length','diameter',
                  'alloy','cast_qty','total_weight','degass','cast_shift','cast_speed',
                  'Mg','Si','Fe','Cu','Cr','Mn','Zn','Ti','Bo',
                  'Mg_HL','Si_HL','Fe_HL','Cu_HL','Cr_HL','Mn_HL','Zn_HL','Ti_HL','Bo_HL']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.today()
        
    
