from django.forms import ModelForm
from django import forms
from .models import BillAddress, ShipAddress, CustomerName



class ShipAddressForm(ModelForm): 
    

    class Meta:
        model = ShipAddress
        fields = ['ship_address','ship_number']



class BillAddressForm(ModelForm):

    
    

    class Meta:
        model = BillAddress
        fields = ['bill_address','bill_number']
    
   
class CustomerNameForm(ModelForm):

    
    

    class Meta:
        model = CustomerName
        fields = ['customer_name','customer_number']


   
