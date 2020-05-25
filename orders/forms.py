from django.forms import ModelForm
from django import forms
from .models import *
from . import formsAddress
from django.utils.timezone import datetime


class OrderForm(ModelForm):
    
    OPTIONS = (
        ('',''),
        ('Yes','Y'),
        ('No','N'),
    )
    
    OPTIONS2 = (
        ('Confirm', 'Confirm'),
        ('Extrusion', 'Extrusion'),
        ('Fabrication', 'Fabrication'),
        ('Anodizing', 'Anodizing'),
        ('Shipping', 'Shipping'),
        ('Cancelled', 'Cancelled')
    )
    OPTIONS3 = (
        ('',''),
        ('O','O'),
        ('S','S'),
    )
    OPTIONS4 = (
        ('',''),
        ('A','A'),
        ('R','R'),
    )
    OPTIONS5 = (
        ('',''),
        ('RE','RE'),
        ('CM','CM'),
    )
    OPTIONS6 = (
        ('',''),
        ('02','02'),
        ('03','03'),
        ('04','04'),
        ('05','05'),
        ('06','06'),
    )

    OPTIONS7 = (
        ('Pending Payment', 'Pending Payment'),
        ('Payment Received', 'Payment Received'),
    )

    OPTIONS8 = (('',''),('Shipped','Shipped'),('Not Shipped','Not Shipped'),('Shipping Finished','Shipping finished'),)

 

    order_status = forms.TypedChoiceField(required=False, choices=OPTIONS2, widget=forms.RadioSelect)
    order_received = forms.ChoiceField(choices=OPTIONS)
    price_method = forms.ChoiceField(choices=OPTIONS3)
    surcharge = forms.ChoiceField(choices=OPTIONS)
    A_R_credit = forms.ChoiceField(choices=OPTIONS4)
    fax_ASN = forms.ChoiceField(choices=OPTIONS)
    email_ASN = forms.ChoiceField(choices=OPTIONS)
    order_type = forms.ChoiceField(choices=OPTIONS5)
    customer_id = forms.ModelChoiceField(queryset=CustomerName.objects.filter(active='1'), empty_label='')
    billAddress_id = forms.ModelChoiceField(queryset=BillAddress.objects.filter(active='1'), empty_label='')
    shipAddress_id = forms.ModelChoiceField(queryset=ShipAddress.objects.filter(active='1'), empty_label='')
    #line_id = forms.ModelChoiceField(queryset=Line.objects.filter(active='1'), empty_label='')
    payment_status =forms.TypedChoiceField(initial="Pending Payment",required=False, choices=OPTIONS7, widget=forms.RadioSelect)
    shipping_status = forms.ChoiceField(choices=OPTIONS8,required=False)
    extrusion_completed = forms.TypedChoiceField(required=False, choices=OPTIONS, widget=forms.RadioSelect)
    shipping_completed = forms.TypedChoiceField(required=False, choices=OPTIONS, widget=forms.RadioSelect)
    fabrication_completed = forms.TypedChoiceField(required=False, choices=OPTIONS, widget=forms.RadioSelect)
    anodizing_completed = forms.TypedChoiceField(required=False, choices=OPTIONS, widget=forms.RadioSelect)
    
    
    class Meta:
        model = Order
        fields = ['line','workorder_number','total_quantity','backorder_quantity','shipping_quantity','total_weight','backorder_weight',
                  'die_number','part_number','required_date','freight','quote','contract','order_status','order_value',
                  'order_received', 'price_method', 'surcharge', 'A_R_credit', 'fax_ASN', 'email_ASN', 'order_type',
                  'order_number', 'order_type', 'ordered_date', 'price_details', 'kit_details', 'ship_via', 'attention',
                  'ship_instructions', 'F_O_B', 'warehouse', 'sales_rep', 'product_line', 'COS_project', 'sales_account',
                  'order_value', 'staus_number', 'contact_name', 'phone_number', 'ship_cond', 'credit_control', 'ASN_contact',
                  'ASN_title', 'ASN_fax_num', 'email_addr', 'customer_id', 'billAddress_id', 'shipAddress_id','payment_status','amount_received',
                  'anodizing_date','anodizing_shift','anodizing_load','anodizing_racked_by','anodizing_bar_number','anodizing_code','anodizing_quantity','anodizing_outside_perimeter','anodizing_length','anodizing_square_feet',
                  'shipping_status','shipping_date','shipping_weight','shipping_due','extrusion_completed','shipping_completed', 'fabrication_completed','anodizing_completed']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordered_date'].initial = datetime.today()
        
        self.fields['order_received'].initial = 'Yes'
        self.fields['order_type'].initial = 'RE'
        self.fields['price_method'].initial = 'O'
        self.fields['freight'].initial =  '02'
        self.fields['price_details'].initial =  ''
        self.fields['kit_details'].initial =  ''
        self.fields['quote'].initial =  ''
        self.fields['contract'].initial =  0

        self.fields['warehouse'].initial = '00'
        self.fields['staus_number'].initial = 2
        self.fields['ship_cond'].initial = 0
        self.fields['ship_via'].initial = 'BEST WAY'
        self.fields['F_O_B'].initial = 'SHIP POINT'
        self.fields['COS_project'].initial = 4200100
        self.fields['sales_account'].initial = 3200130

        self.fields['surcharge'].initial = 'No'
        self.fields['A_R_credit'].initial = 'A'
        self.fields['fax_ASN'].initial = 'No'
        self.fields['email_ASN'].initial = 'Yes'
        self.fields['amount_received'].initial = 0
        



    
