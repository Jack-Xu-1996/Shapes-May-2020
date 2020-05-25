from django.forms import ModelForm
from django import forms
from .models import PurchaseReport

class PurchasereportForm(ModelForm):
    
    class Meta:
        model = PurchaseReport
        fields = ['P_O','Vendor_No','Vendor_Name','line','Partno','Partdescr',
                  'GL_Accountno','Datepromised','Qtyonorder','Price','Line_Amount',
                  'Requestedby','Buyer','Status','Projectno','Project_Desc']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
