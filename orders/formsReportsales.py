from django.forms import ModelForm
from django import forms
from .models import SalesReport

class SalesreportForm(ModelForm):

    OPTIONS = (
        ('',''),
        ('BL','BL'),
        ('CL','CL'),
        ('DA','DA'),
        ('S1','S1'),
        ('S2','S2'),
        ('S3','S3'),
        ('S4','S4'),
    )
    
    OPTIONS2 = (
        ('',''),
        ('RE', 'RE'),
        ('CM', 'CM'),
        ('01', '01'),
        ('02', '02'),
    )
    OPTIONS3 = (
        ('',''),
        ('AS','AS'),
        ('AY','AY'),
        ('CM','CM'),
        ('PC','PC'),
        ('KT','KT'),        
    )
    OPTIONS4 = (
        ('',''),
        ('CMET','CMET'),
        ('FIN','FIN'),
        ('WIP','WIP'),
    )

    Press = forms.ChoiceField(choices=OPTIONS)
    Ordertype = forms.ChoiceField(choices=OPTIONS2)
    Unitofmeas = forms.ChoiceField(choices=OPTIONS3)
    Productline = forms.ChoiceField(choices=OPTIONS4)
    
    class Meta:
        model = SalesReport
        fields = ['Customerno','Companyname','Die_Number','Invoiceno','Salesorderno',
                  'Lineno_Alt','Partno','Partdescr','Dateshipped','Invoicedate',
                  'Qty_Shipped','Calc_Actual_Wgt','Calc_Theor_Wgt','Calc_Price',
                  'Extrusion_Revenue','Price_per_Lb','Fabrication_Lbs','Fabrication_Revenue',
                  'Paint_Lbs','Paint_Revenue','Anodizing_Sq_Ft','Anodizing_Revenue','Ingot_Price','Shiptono',
                  'Ship_To_State','RSM','RSM_name','Press','Ordertype','Unitofmeas','Productline']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
