from django.forms import ModelForm
from django import forms
from .models import *
from . import formsAccount, formsPart
from django.utils.timezone import datetime

class PurchaseForm(ModelForm):
    
    OPTIONS = (
        ('',''),
        ('Yes','Y'),
        ('No','N'),
    )
    
    OPTIONS2 = (
        ('',''),
        ('C', 'C'),
        ('F', 'F'),
        ('R', 'R'),
        ('S', 'S'),
    )
    OPTIONS3 = (
        ('',''),
        ('OP','OP'),
        ('F','F'),
        ('O','O'),
        ('M','M'),
        ('P','P'),        
    )
    OPTIONS4 = (
        ('',''),
        ('fz','(fz)FENG ZHU'),
        ('jc','(JC)JIM CACKOWSKI'),
    )
    OPTIONS5 = (
        ('Pending Payment', 'Pending Payment'),
         ('Partially Paid', 'Partially Paid'),
        ('Payment Complete', 'Payment Complete'),
    )
    
    OPTIONS6 = (
        ('',''),
        ('Pending Arrival','Pending Arrival'),
        ('Arrived','Arrived'),
    )

    requisition_status = forms.ChoiceField(choices=OPTIONS2)
    purchase_type = forms.ChoiceField(choices=OPTIONS3)
    red_req = forms.ChoiceField(choices=OPTIONS)
    ready_for_approval = forms.ChoiceField(choices=OPTIONS)
    approved_yn = forms.ChoiceField(choices=OPTIONS)
    buyer = forms.ChoiceField(choices=OPTIONS4)
    part_id = forms.ModelChoiceField(queryset=Part.objects.filter(active='1'), empty_label='')
    account_id = forms.ModelChoiceField(queryset=Account.objects.filter(active='1'), empty_label='')
    #line_id = forms.ModelChoiceField(queryset=Line.objects.filter(active='1'), empty_label='')
    arrival_status = forms.ChoiceField(choices=OPTIONS6,required=False)
    payment_status =forms.TypedChoiceField(initial="Pending Payment",required=False, choices=OPTIONS5, widget=forms.RadioSelect)

    class Meta:
        model = Purchase
        fields = ['requisition_number','requested_by','entry_date','project_number',
                  'project_description','header_comments','line','quantity','required_date',
                  'vendor_one','vendor_two','vendor_three','unit_price_one','unit_price_two',
                  'unit_price_three','total','internal_comments','on_hand','on_order',
                  'reorder_point','supplier','purchase_quantity','requisition_status',
                  'purchase_type','red_req','ready_for_approval','approved_yn','buyer',
                  'part_id','account_id','payment_status','amount_paid','arrival_status']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entry_date'].initial = datetime.today()
        
