from django.forms import ModelForm
from django import forms
from .models import Line


class OrderLine(ModelForm):
    OPTIONS = (
        ('',''),
        ('02','02'),
        ('03','03'),
        ('04','04'),
        ('05','05'),
        ('06','06'),
    )
    stat = forms.ChoiceField(choices=OPTIONS)
    
    class Meta:
        model = Line 
        fields = ['order_number','customer_number', 'customer_name', 'cat', 'ship_days', 'travel_days',
                    'order_total', 'estimated_costs', 'line_number','part_number','description','whse','alloc','qty_order','qty_avail','required_date',
                    'promised_date','unit_price','ship_tolerance_min','ship_tolerance_max','uos','price_book','stat']

