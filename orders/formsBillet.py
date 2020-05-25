from django.forms import ModelForm
from django import forms
from .models import Billet
from django.utils.timezone import datetime

class BilletForm(ModelForm):
    
    class Meta:
        model = Billet 
        fields = ['S1_7_rack','S1_7_loose','S1_32_7_rack','S1_32_7_loose','S1_30_7_rack','S1_30_7_loose',
                  'S1_28_7_rack','S1_28_7_loose','S1_26_7_rack','S1_26_7_loose','S1_24_7_rack','S1_24_7_loose',
                  'S1_22_7_rack','S1_22_7_loose','SA_32_7_rack','SA_32_7_loose','SA_31_7_rack','SA_31_7_loose',
                  'SA_30_7_rack','SA_30_7_loose','SA_29_7_rack','SA_29_7_loose','SA_28_7_rack','SA_28_7_loose',
                  'SA_27_7_rack','SA_27_7_loose','SA_26_7_rack','SA_26_7_loose','SA_24_7_rack','SA_24_7_loose',
                  'SA_22_7_rack','SA_22_7_loose','SA_20_7_rack','SA_20_7_loose','L_24_7_rack','L_24_7_loose',
                  'L_28_7_rack','L_28_7_loose','L_30_7_rack','L_30_7_loose','L_32_7_rack','L_32_7_loose',
                  'SA_22_11_rack','SA_22_11_loose','SA_24_11_rack','SA_24_11_loose','SA_26_11_rack','SA_26_11_loose',
                  'SA_28_11_rack','SA_28_11_loose','SA_30_11_rack','SA_30_11_loose','SA_32_11_rack','SA_32_11_loose',
                  'SA_34_11_rack','SA_34_11_loose','L_30_11_rack','L_30_11_loose','L_34_11_rack','L_34_11_loose',
                  'L_32_11_rack','L_32_11_loose','AP_22_11_rack','AP_22_11_loose','AP_26_11_rack','AP_26_11_loose',
                  'AP_30_11_rack','AP_30_11_loose','AP_32_11_rack','AP_32_11_loose','P1_34_11_rack','P1_34_11_loose',
                  'P1_32_11_rack','P1_32_11_loose','P1_30_11_rack','P1_30_11_loose','P1_28_11_rack','P1_28_11_loose',
                  'P1_26_11_rack','P1_26_11_loose','P1_24_11_rack','P1_24_11_loose','P1_22_11_rack','P1_22_11_loose',
                  'L_21_14_rack','L_21_14_loose','A_20_14_rack','A_20_14_loose','A_22_14_rack','A_22_14_loose',
                  'A_24_14_rack','A_24_14_loose','A_30_14_rack','A_30_14_loose','P1_20_14_rack','P1_20_14_loose',
                  'P1_22_14_rack','P1_22_14_loose','P1_24_14_rack','P1_24_14_loose','P1_26_14_rack','P1_26_14_loose',
                  'P1_28_14_rack','P1_28_14_loose','P1_30_14_rack','P1_30_14_loose','P1_32_14_rack','P1_32_14_loose',
                  'P1_34_14_rack','P1_34_14_loose','P1_36_14_rack','P1_36_14_loose','P1_38_14_rack','P1_38_14_loose',
                  'SA_20_9_rack','SA_20_9_loose','SA_22_9_rack','SA_22_9_loose','SA_24_9_rack','SA_24_9_loose',
                  'SA_25_9_rack','SA_25_9_loose','SA_26_9_rack','SA_26_9_loose','SA_27_9_rack','SA_27_9_loose',
                  'SA_28_9_rack','SA_28_9_loose','SA_29_9_rack','SA_29_9_loose','SA_30_9_rack','SA_30_9_loose',
                  'SA_31_9_rack','SA_31_9_loose','SA_32_9_rack','SA_32_9_loose','SA_34_9_rack','SA_34_9_loose',
                  'L_32_9_rack','L_32_9_loose','L_34_9_rack','L_34_9_loose','L_30_9_rack','L_30_9_loose',
                  'L_22_9_rack','L_22_9_loose','L_24_9_rack','L_24_9_loose','L_28_9_rack','L_28_9_loose',
                  'P1_20_9_rack','P1_20_9_loose','P1_22_9_rack','P1_22_9_loose','P1_24_9_rack','P1_24_9_loose',
                  'P1_26_9_rack','P1_26_9_loose','P1_28_9_rack','P1_28_9_loose','P1_30_9_rack','P1_30_9_loose',
                  'P1_32_9_rack','P1_32_9_loose','P1_34_9_rack','P1_34_9_loose','P1_36_9_rack','P1_36_9_loose',
                  'BB_30_9_rack','BB_30_9_loose','BB_34_9_rack','BB_34_9_loose','Date']
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Date'].initial = datetime.today()
'''
        self.fields['S1_7_rack'].initial =  0
        self.fields['S1_7_loose'].initial =  0
        self.fields['S1_32_7_rack'].initial =  0
        self.fields['S1_32_7_loose'].initial =  0
        self.fields['S1_30_7_rack'].initial =  0
        self.fields['S1_30_7_loose'].initial =  0
        self.fields['S1_28_7_rack'].initial =  0
        self.fields['S1_28_7_loose'].initial =  0
        self.fields['S1_26_7_rack'].initial =  0
        self.fields['S1_26_7_loose'].initial =  0
        self.fields['S1_24_7_rack'].initial =  0
        self.fields['S1_24_7_loose'].initial =  0
        self.fields['S1_22_7_rack'].initial =  0
        self.fields['S1_22_7_loose'].initial =  0
        self.fields['SA_32_7_rack'].initial =  0
        self.fields['SA_32_7_loose'].initial =  0
        self.fields['SA_31_7_rack'].initial =  0
        self.fields['SA_31_7_loose'].initial =  0
        self.fields['SA_30_7_rack'].initial =  0
        self.fields['SA_30_7_loose'].initial =  0
        self.fields['SA_29_7_rack'].initial =  0
        self.fields['SA_29_7_loose'].initial =  0
        self.fields['SA_28_7_rack'].initial =  0
        self.fields['SA_28_7_loose'].initial =  0
        self.fields['SA_27_7_rack'].initial =  0
        self.fields['SA_27_7_loose'].initial =  0
        self.fields['SA_26_7_rack'].initial =  0
        self.fields['SA_26_7_loose'].initial =  0
        self.fields['SA_24_7_rack'].initial =  0
        self.fields['SA_24_7_loose'].initial =  0
        self.fields['SA_22_7_rack'].initial =  0
        self.fields['SA_22_7_loose'].initial =  0
        self.fields['SA_20_7_rack'].initial =  0
        self.fields['SA_20_7_loose'].initial =  0
        self.fields['L_24_7_rack'].initial =  0
        self.fields['L_24_7_loose'].initial =  0
        self.fields['L_28_7_rack'].initial =  0
        self.fields['L_28_7_loose'].initial =  0
        self.fields['L_30_7_rack'].initial =  0
        self.fields['L_30_7_loose'].initial =  0
        self.fields['L_32_7_rack'].initial =  0
        self.fields['L_32_7_loose'].initial =  0
        self.fields['SA_22_11_rack'].initial =  0
        self.fields['SA_22_11_loose'].initial =  0
        self.fields['SA_24_11_rack'].initial =  0
        self.fields['SA_24_11_loose'].initial =  0
        self.fields['SA_26_11_rack'].initial =  0
        self.fields['SA_26_11_loose'].initial =  0
        self.fields['SA_28_11_rack'].initial =  0
        self.fields['SA_28_11_loose'].initial =  0
        self.fields['SA_30_11_rack'].initial =  0
        self.fields['SA_30_11_loose'].initial =  0
        self.fields['SA_32_11_rack'].initial =  0
        self.fields['SA_32_11_loose'].initial =  0
        self.fields['SA_34_11_rack'].initial =  0
        self.fields['SA_34_11_loose'].initial =  0
        self.fields['L_30_11_rack'].initial =  0
        self.fields['L_30_11_loose'].initial =  0
        self.fields['L_34_11_rack'].initial =  0
        self.fields['L_34_11_loose'].initial =  0
        self.fields['L_32_11_rack'].initial =  0
        self.fields['L_32_11_loose'].initial =  0
        self.fields['AP_22_11_rack'].initial =  0
        self.fields['AP_22_11_loose'].initial =  0
        self.fields['AP_26_11_rack'].initial =  0
        self.fields['AP_26_11_loose'].initial =  0
        self.fields['AP_30_11_rack'].initial =  0
        self.fields['AP_30_11_loose'].initial =  0
        self.fields['AP_32_11_rack'].initial =  0
        self.fields['AP_32_11_loose'].initial =  0
        self.fields['P1_34_11_rack'].initial =  0
        self.fields['P1_34_11_loose'].initial =  0
        self.fields['P1_32_11_rack'].initial =  0
        self.fields['P1_32_11_loose'].initial =  0
        self.fields['P1_30_11_rack'].initial =  0
        self.fields['P1_30_11_loose'].initial =  0
        self.fields['P1_28_11_rack'].initial =  0
        self.fields['P1_28_11_loose'].initial =  0
        self.fields['P1_26_11_rack'].initial =  0
        self.fields['P1_26_11_loose'].initial =  0
        self.fields['P1_24_11_rack'].initial =  0
        self.fields['P1_24_11_loose'].initial =  0
        self.fields['P1_22_11_rack'].initial =  0
        self.fields['P1_22_11_loose'].initial =  0
        self.fields['L_21_14_rack'].initial =  0
        self.fields['L_21_14_loose'].initial =  0
        self.fields['A_20_14_rack'].initial =  0
        self.fields['A_20_14_loose'].initial =  0
        self.fields['A_22_14_rack'].initial =  0
        self.fields['A_22_14_loose'].initial =  0
        self.fields['A_24_14_rack'].initial =  0
        self.fields['A_24_14_loose'].initial =  0
        self.fields['A_30_14_rack'].initial =  0
        self.fields['A_30_14_loose'].initial =  0
        self.fields['P1_20_14_rack'].initial =  0
        self.fields['P1_20_14_loose'].initial =  0
        self.fields['P1_22_14_rack'].initial =  0
        self.fields['P1_22_14_loose'].initial =  0
        self.fields['P1_24_14_rack'].initial =  0
        self.fields['P1_24_14_loose'].initial =  0
        self.fields['P1_26_14_rack'].initial =  0
        self.fields['P1_26_14_loose'].initial =  0
        self.fields['P1_28_14_rack'].initial =  0
        self.fields['P1_28_14_loose'].initial =  0
        self.fields['P1_30_14_rack'].initial =  0
        self.fields['P1_30_14_loose'].initial =  0
        self.fields['P1_32_14_rack'].initial =  0
        self.fields['P1_32_14_loose'].initial =  0
        self.fields['P1_34_14_rack'].initial =  0
        self.fields['P1_34_14_loose'].initial =  0
        self.fields['P1_36_14_rack'].initial =  0
        self.fields['P1_36_14_loose'].initial =  0
        self.fields['P1_38_14_rack'].initial =  0
        self.fields['P1_38_14_loose'].initial =  0
        self.fields['SA_20_9_rack'].initial =  0
        self.fields['SA_20_9_loose'].initial =  0
        self.fields['SA_22_9_rack'].initial =  0
        self.fields['SA_22_9_loose'].initial =  0
        self.fields['SA_24_9_rack'].initial =  0
        self.fields['SA_24_9_loose'].initial =  0
        self.fields['SA_25_9_rack'].initial =  0
        self.fields['SA_25_9_loose'].initial =  0
        self.fields['SA_26_9_rack'].initial =  0
        self.fields['SA_26_9_loose'].initial =  0
        self.fields['SA_27_9_rack'].initial =  0
        self.fields['SA_27_9_loose'].initial =  0
        self.fields['SA_28_9_rack'].initial =  0
        self.fields['SA_28_9_loose'].initial =  0
        self.fields['SA_29_9_rack'].initial =  0
        self.fields['SA_29_9_loose'].initial =  0
        self.fields['SA_30_9_rack'].initial =  0
        self.fields['SA_30_9_loose'].initial =  0
        self.fields['SA_31_9_rack'].initial =  0
        self.fields['SA_31_9_loose'].initial =  0
        self.fields['SA_32_9_rack'].initial =  0
        self.fields['SA_32_9_loose'].initial =  0
        self.fields['SA_34_9_rack'].initial =  0
        self.fields['SA_34_9_loose'].initial =  0
        self.fields['L_32_9_rack'].initial =  0
        self.fields['L_32_9_loose'].initial =  0
        self.fields['L_34_9_rack'].initial =  0
        self.fields['L_34_9_loose'].initial =  0
        self.fields['L_30_9_rack'].initial =  0
        self.fields['L_30_9_loose'].initial =  0
        self.fields['L_22_9_rack'].initial =  0
        self.fields['L_22_9_loose'].initial =  0
        self.fields['L_20_9_rack'].initial =  0
        self.fields['L_20_9_loose'].initial =  0
        self.fields['L_28_9_rack'].initial =  0
        self.fields['L_28_9_loose'].initial =  0
        self.fields['P1_20_9_rack'].initial =  0
        self.fields['P1_20_9_loose'].initial =  0
        self.fields['P1_22_9_rack'].initial =  0
        self.fields['P1_22_9_loose'].initial =  0
        self.fields['P1_24_9_rack'].initial =  0
        self.fields['P1_24_9_loose'].initial =  0
        self.fields['P1_26_9_rack'].initial =  0
        self.fields['P1_26_9_loose'].initial =  0
        self.fields['P1_28_9_rack'].initial =  0
        self.fields['P1_28_9_loose'].initial =  0
        self.fields['P1_30_9_rack'].initial =  0
        self.fields['P1_30_9_loose'].initial =  0
        self.fields['P1_32_9_rack'].initial =  0
        self.fields['P1_32_9_loose'].initial =  0
        self.fields['P1_34_9_rack'].initial =  0
        self.fields['P1_34_9_loose'].initial =  0
        self.fields['P1_36_9_rack'].initial =  0
        self.fields['P1_36_9_loose'].initial =  0
        self.fields['BB_30_9_rack'].initial =  0
        self.fields['BB_30_9_loose'].initial =  0
        self.fields['BB_34_9_rack'].initial =  0
        self.fields['BB_34_9_loose'].initial =  0
'''
