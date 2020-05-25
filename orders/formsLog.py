from django.forms import ModelForm
from django import forms
from .models import Log
from django.utils.timezone import datetime

class LogForm(ModelForm):
    
    class Meta:
        model = Log 
        fields = ['Date','Cropped_S1_7_len1','Cropped_S1_7_len2','Cropped_S1_7_len3','Cropped_S1_7_num1','Cropped_S1_7_num2','Cropped_S1_7_num3',
    'Cropped_SA_7_len1','Cropped_SA_7_len2','Cropped_SA_7_len3','Cropped_SA_7_num1','Cropped_SA_7_num2','Cropped_SA_7_num3',
    'Cropped_L_7_len1','Cropped_L_7_len2','Cropped_L_7_len3','Cropped_L_7_num1','Cropped_L_7_num2','Cropped_L_7_num3',
    'Cropped_BB_7_len1','Cropped_BB_7_len2','Cropped_BB_7_len3','Cropped_BB_7_num1','Cropped_BB_7_num2','Cropped_BB_7_num3',
    'Cropped_1350_7_len1','Cropped_1350_7_len2','Cropped_1350_7_len3','Cropped_1350_7_num1','Cropped_1350_7_num2','Cropped_1350_7_num3',
    'Cropped_other_7_len1','Cropped_other_7_len2','Cropped_other_7_len3','Cropped_other_7_num1','Cropped_other_7_num2','Cropped_other_7_num3',
    'Cropped_BB_16_len1','Cropped_BB_16_len2','Cropped_BB_16_len3','Cropped_BB_16_num1','Cropped_BB_16_num2','Cropped_BB_16_num3',
    'Cropped_SA_16_len1','Cropped_SA_16_len2','Cropped_SA_16_len3','Cropped_SA_16_num1','Cropped_SA_16_num2','Cropped_SA_16_num3',
    'Cropped_S1_16_len1','Cropped_S1_16_len2','Cropped_S1_16_len3','Cropped_S1_16_num1','Cropped_S1_16_num2','Cropped_S1_16_num3',
    'Cropped_P1_16_len1','Cropped_P1_16_len2','Cropped_P1_16_len3','Cropped_P1_16_num1','Cropped_P1_16_num2','Cropped_P1_16_num3',
    'Cropped_L_16_len1','Cropped_L_16_len2','Cropped_L_16_len3','Cropped_L_16_num1','Cropped_L_16_num2','Cropped_L_16_num3',
    'Cropped_M_16_len1','Cropped_M_16_len2','Cropped_M_16_len3','Cropped_M_16_num1','Cropped_M_16_num2','Cropped_M_16_num3',
    'Homo_S1_7_len1','Homo_S1_7_len2','Homo_S1_7_len3','Homo_S1_7_num1','Homo_S1_7_num2','Homo_S1_7_num3',
    'Homo_SA_7_len1','Homo_SA_7_len2','Homo_SA_7_len3','Homo_SA_7_num1','Homo_SA_7_num2','Homo_SA_7_num3',
    'Homo_6005A_7_len1','Homo_6005A_7_len2','Homo_6005A_7_len3','Homo_6005A_7_num1','Homo_6005A_7_num2','Homo_6005A_7_num3',
    'Homo_P1_9_len1','Homo_P1_9_len2','Homo_P1_9_len3','Homo_P1_9_num1','Homo_P1_9_num2','Homo_P1_9_num3',
    'Homo_SA_9_len1','Homo_SA_9_len2','Homo_SA_9_len3','Homo_SA_9_num1','Homo_SA_9_num2','Homo_SA_9_num3',
    'Homo_L_9_len1','Homo_L_9_len2','Homo_L_9_len3','Homo_L_9_num1','Homo_L_9_num2','Homo_L_9_num3',
    'Homo_L_11_len1','Homo_L_11_len2','Homo_L_11_len3','Homo_L_11_num1','Homo_L_11_num2','Homo_L_11_num3',
    'Homo_SA_11_len1','Homo_SA_11_len2','Homo_SA_11_len3','Homo_SA_11_num1','Homo_SA_11_num2','Homo_SA_11_num3',
    'Homo_AP_11_len1','Homo_AP_11_len2','Homo_AP_11_len3','Homo_AP_11_num1','Homo_AP_11_num2','Homo_AP_11_num3',
    'Homo_M1_11_len1','Homo_M1_11_len2','Homo_M1_11_len3','Homo_M1_11_num1','Homo_M1_11_num2','Homo_M1_11_num3',
    'Homo_P1_11_len1','Homo_P1_11_len2','Homo_P1_11_len3','Homo_P1_11_num1','Homo_P1_11_num2','Homo_P1_11_num3',
    'Homo_L_16_len1','Homo_L_16_len2','Homo_L_16_len3','Homo_L_16_num1','Homo_L_16_num2','Homo_L_16_num3',
    'Homo_M1_16_len1','Homo_M1_16_len2','Homo_M1_16_len3','Homo_M1_16_num1','Homo_M1_16_num2','Homo_M1_16_num3',
    'Homo_BB_16_len1','Homo_BB_16_len2','Homo_BB_16_len3','Homo_BB_16_num1','Homo_BB_16_num2','Homo_BB_16_num3',
    'Homo_SA_16_len1','Homo_SA_16_len2','Homo_SA_16_len3','Homo_SA_16_num1','Homo_SA_16_num2','Homo_SA_16_num3',
    'Homo_S1_16_len1','Homo_S1_16_len2','Homo_S1_16_len3','Homo_S1_16_num1','Homo_S1_16_num2','Homo_S1_16_num3',
    'Homo_P1_16_len1','Homo_P1_16_len2','Homo_P1_16_len3','Homo_P1_16_num1','Homo_P1_16_num2','Homo_P1_16_num3',
    'Unhomo_S1_7_len1','Unhomo_S1_7_len2','Unhomo_S1_7_len3','Unhomo_S1_7_num1','Unhomo_S1_7_num2','Unhomo_S1_7_num3',
    'Unhomo_SA_7_len1','Unhomo_SA_7_len2','Unhomo_SA_7_len3','Unhomo_SA_7_num1','Unhomo_SA_7_num2','Unhomo_SA_7_num3',
    'Unhomo_6005A_7_len1','Unhomo_6005A_7_len2','Unhomo_6005A_7_len3','Unhomo_6005A_7_num1','Unhomo_6005A_7_num2','Unhomo_6005A_7_num3',
    'Unhomo_P1_9_len1','Unhomo_P1_9_len2','Unhomo_P1_9_len3','Unhomo_P1_9_num1','Unhomo_P1_9_num2','Unhomo_P1_9_num3',
    'Unhomo_SA_9_len1','Unhomo_SA_9_len2','Unhomo_SA_9_len3','Unhomo_SA_9_num1','Unhomo_SA_9_num2','Unhomo_SA_9_num3',
    'Unhomo_L_9_len1','Unhomo_L_9_len2','Unhomo_L_9_len3','Unhomo_L_9_num1','Unhomo_L_9_num2','Unhomo_L_9_num3',
    'Unhomo_L_11_len1','Unhomo_L_11_len2','Unhomo_L_11_len3','Unhomo_L_11_num1','Unhomo_L_11_num2','Unhomo_L_11_num3',
    'Unhomo_SA_11_len1','Unhomo_SA_11_len2','Unhomo_SA_11_len3','Unhomo_SA_11_num1','Unhomo_SA_11_num2','Unhomo_SA_11_num3',
    'Unhomo_AP_11_len1','Unhomo_AP_11_len2','Unhomo_AP_11_len3','Unhomo_AP_11_num1','Unhomo_AP_11_num2','Unhomo_AP_11_num3',
    'Unhomo_M1_11_len1','Unhomo_M1_11_len2','Unhomo_M1_11_len3','Unhomo_M1_11_num1','Unhomo_M1_11_num2','Unhomo_M1_11_num3',
    'Unhomo_P1_11_len1','Unhomo_P1_11_len2','Unhomo_P1_11_len3','Unhomo_P1_11_num1','Unhomo_P1_11_num2','Unhomo_P1_11_num3',
    'Unhomo_L_16_len1','Unhomo_L_16_len2','Unhomo_L_16_len3','Unhomo_L_16_num1','Unhomo_L_16_num2','Unhomo_L_16_num3',
    'Unhomo_M1_16_len1','Unhomo_M1_16_len2','Unhomo_M1_16_len3','Unhomo_M1_16_num1','Unhomo_M1_16_num2','Unhomo_M1_16_num3',
    'Unhomo_BB_16_len1','Unhomo_BB_16_len2','Unhomo_BB_16_len3','Unhomo_BB_16_num1','Unhomo_BB_16_num2','Unhomo_BB_16_num3',
    'Unhomo_SA_16_len1','Unhomo_SA_16_len2','Unhomo_SA_16_len3','Unhomo_SA_16_num1','Unhomo_SA_16_num2','Unhomo_SA_16_num3',
    'Unhomo_S1_16_len1','Unhomo_S1_16_len2','Unhomo_S1_16_len3','Unhomo_S1_16_num1','Unhomo_S1_16_num2','Unhomo_S1_16_num3',
    'Unhomo_P1_16_len1','Unhomo_P1_16_len2','Unhomo_P1_16_len3','Unhomo_P1_16_num1','Unhomo_P1_16_num2','Unhomo_P1_16_num3',
]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Date'].initial = datetime.today()
