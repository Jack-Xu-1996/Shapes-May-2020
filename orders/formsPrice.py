from django.forms import ModelForm
from django import forms
from .models import Price
from django.utils.timezone import datetime

class PriceForm(ModelForm):
    
   
    class Meta:
        model = Price
        fields = ['qty_order','price_book','total_per_piece_lbs','total_per_piece_sqft',
                  'total_per_piece_lnft','die_num','die_type','die_unit_price',
                  'billet_alloy_unit_price', 'fabrication_unit_price','paint_lbs_unit_price',
                  'paint_sqft_unit_price','anodizing_unit_price','anodizing_qua','thermal_break_unit_price',
                  'exagrip_unit_price','masking_unit_price','packaging_unit_price','price_time',
                  'ingot_price','conversion_factor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['die_unit_price'].initial =  0.12
        #self.fields['billet_alloy_unit_price'].initial =  1.652
        self.fields['fabrication_unit_price'].initial =  0
        self.fields['paint_lbs_unit_price'].initial =  0
        self.fields['paint_sqft_unit_price'].initial =  0
        self.fields['thermal_break_unit_price'].initial =  0
        self.fields['exagrip_unit_price'].initial =  0
        self.fields['masking_unit_price'].initial =  0
        self.fields['ingot_price'].initial =  0.972
        self.fields['conversion_factor'].initial =  0




        
