from django.db import models
import math
from django.contrib.auth.models import User
#from __future__ import unicode_literals


     

class Line(models.Model):
    order_number = models.IntegerField(default=False, blank=True, null=True);
    customer_number = models.IntegerField(default=False, blank=True, null=True); 
    customer_name = models.CharField(max_length=50, blank=True, null=True);
    cat = models.IntegerField(default=False, blank=True, null=True); 
    ship_days = models.IntegerField(default=False, blank=True, null=True); 
    travel_days = models.IntegerField(default=False, blank=True, null=True); 
    order_total = models.IntegerField(default=False, blank=True, null=True); 
    estimated_costs = models.IntegerField(default=False, blank=True, null=True);
    
    line_number = models.IntegerField(default=False, blank=False, null=True); 
    part_number = models.CharField(max_length=50, blank=True, null=True);
    description = models.TextField(blank=True, null=False);
    whse = models.IntegerField(blank=True, null=True);
    alloc = models.TextField(blank=True, null=True);
    qty_order = models.IntegerField(default=False, blank=False, null=True); 
    qty_avail = models.IntegerField(default=False, blank=True, null=True); 
    required_date = models.DateField(blank=False);
    promised_date = models.DateField(blank=True);
    unit_price = models.FloatField(default=False, blank=False, null=True)
    ship_tolerance_min = models.IntegerField(default=False, blank=True, null=True); 
    ship_tolerance_max = models.IntegerField(default=False, blank=True, null=True); 
    uos = models.IntegerField(default=False, blank=True, null=True); 
    price_book = models.IntegerField(default=False, blank=True, null=True); 
    stat = models.CharField(max_length=50, null=True);
    #active = models.IntegerField(default='1')
    '''
    def __str__(self):
        return '%s %s %d ' % (self.part_number, self.description, self.qty_order)
    '''


class Price(models.Model):
    
    qty_order = models.IntegerField(default=False, blank=False, null=True); 
    price_book = models.IntegerField(default=False, blank=False, null=True); 
    total_per_piece_lbs = models.FloatField(default=False, blank=False, null=True);
    total_per_piece_sqft = models.FloatField(default=False, blank=False, null=True);
    total_per_piece_lnft = models.FloatField(default=False, blank=False, null=True);
    die_num = models.IntegerField(default=False, blank=False, null=True); 
    die_type = models.CharField(max_length=50, blank=True, null=True);
    die_unit_price =  models.FloatField(default=False, blank=False, null=True);
    #billet_alloy_num = models.IntegerField(fblank=True, null=True); 
    billet_alloy_unit_price = models.FloatField(default=False, blank=False, null=True);

    fabrication_unit_price = models.FloatField(default=False, blank=False, null=True);

    paint_lbs_unit_price = models.FloatField(default=False, blank=False, null=True);
    
    paint_sqft_unit_price  = models.FloatField(default=False, blank=False, null=True);
    
    anodizing_unit_price = models.FloatField(default=False, blank=False, null=True);
    anodizing_qua = models.FloatField(default=False, blank=False, null=True);
    

    thermal_break_unit_price = models.FloatField(default=False, blank=False, null=True);
    
    exagrip_unit_price = models.FloatField(default=False, blank=False, null=True);
     
    masking_unit_price = models.FloatField(default=False, blank=False, null=True);
     
    packaging_unit_price = models.FloatField(default=False, blank=False, null=True);

    price_time = models.IntegerField(default=False, blank=False, null=True); 

    ingot_price = models.FloatField(default=False, blank=False, null=True);
    conversion_factor = models.FloatField(default=False, blank=False, null=True);
    
    

    @property
    def price_per_piece_die_billet(self):
        return (self.die_unit_price + self.billet_alloy_unit_price)*self.total_per_piece_lbs

    @property
    def price_per_piece_fab(self):
        return self.fabrication_unit_price

    
    @property
    def price_per_piece_paintlbs(self):
        return self.paint_lbs_unit_price

    @property
    def price_per_piece_paintsqft(self):
        return self.paint_sqft_unit_price

    @property
    def price_per_piece_anodizing(self):
        return (self.anodizing_unit_price)*(self.anodizing_qua)

    @property
    def price_per_piece_thermal(self):
        return self.thermal_break_unit_price

    @property
    def price_per_piece_exagrip(self):
        return self.exagrip_unit_price

    @property
    def price_per_piece_masking(self):
        return self.masking_unit_price

    @property
    def price_per_piece_packaging(self):
        return self.packaging_unit_price

    @property
    def total_price(self):
        return (self.die_unit_price + self.billet_alloy_unit_price)*self.total_per_piece_lbs + self.fabrication_unit_price +\
                self.paint_lbs_unit_price + self.paint_sqft_unit_price + (self.anodizing_unit_price)*(self.anodizing_qua) +\
                self.thermal_break_unit_price + self.exagrip_unit_price + self.masking_unit_price + self.packaging_unit_price

    @property
    def total_pounds_ordered(self):
        return (self.total_per_piece_lbs)*self.qty_order



class CustomerName(models.Model):
    customer_name = models.TextField(blank=True);
    customer_number = models.CharField(max_length=50, blank=False, null=False);
    active = models.IntegerField(default='1')

    def __str__(self):
        return '(%s) %s' % (self.customer_number, self.customer_name)

class ShipAddress(models.Model):
    ship_address = models.TextField(blank=True);
    ship_number = models.CharField(max_length=50, blank=False, null=False);
    active = models.IntegerField(default='1')

    def __str__(self):
        return '(%s) %s' % (self.ship_number, self.ship_address)

class BillAddress(models.Model):
    bill_address = models.TextField(blank=True);
    bill_number = models.CharField(max_length=50, blank=False, null=False);
    active = models.IntegerField(default='1')

    def __str__(self):
        return '(%s) %s' % (self.bill_number, self.bill_address)


class Order (models.Model):
    order_number = models.CharField(max_length=50, blank=True, null=True);
    line = models.CharField(max_length=50, blank=True, null=True);
    workorder_number = models.CharField(max_length=50, blank=True, null=True);

    total_quantity = models.IntegerField(blank=True, null=True);
    backorder_quantity = models.IntegerField(blank=True, null=True);
    shipping_quantity = models.IntegerField(blank=True, null=True);
    total_weight = models.FloatField(blank=True, null=True);
    backorder_weight = models.FloatField(blank=True, null=True);
    
    die_number = models.CharField(max_length=50, blank=True, null=True);
    part_number = models.CharField(max_length=50, blank=True, null=True);
    required_date = models.DateField(blank=False, null=False);
    freight = models.CharField(max_length=50, null=True);
    quote = models.CharField(blank=True, max_length=50, null=True);
    contract= models.IntegerField(blank=True, null=True);
    order_status = models.CharField(max_length=50);
    order_value = models.FloatField(blank=True, null=True);

    order_received = models.CharField(max_length=50, null=True);
    price_method = models.CharField(max_length=50, null=True);
    surcharge = models.CharField(max_length=50, null=True);
    A_R_credit = models.CharField(max_length=50, null=True);
    fax_ASN = models.CharField(max_length=50, null=True);
    email_ASN = models.CharField(max_length=50, null=True);
    order_type = models.CharField(max_length=50, null=True);

  
    ordered_date = models.DateField(blank=False, null=True);
    price_details = models.TextField(blank=True, null=True);
    kit_details = models.TextField(blank=True, null=True);
    ship_via = models.TextField(blank=True, null=True);
    attention = models.TextField(blank=True, null=True);
    ship_instructions = models.TextField(blank=True, null=True);
    F_O_B = models.TextField(blank=True, null=True);
    warehouse = models.CharField(max_length=50, blank=True, null=True);
    sales_rep = models.CharField(max_length=50, blank=True, null=True);
    product_line = models.TextField(blank=True, null=True);
    COS_project = models.IntegerField(blank=True, null=True);
    sales_account = models.IntegerField(blank=True, null=True);
    order_value = models.IntegerField(blank=True, null=True);
    staus_number = models.IntegerField(blank=True, null=True);
    contact_name = models.CharField(max_length=50, blank=True, null=True);
    phone_number = models.IntegerField(blank=True, null=True);
    ship_cond = models.IntegerField(blank=True, null=True);
    credit_control = models.IntegerField(blank=True, null=True);
    ASN_contact = models.CharField(max_length=50, blank=True, null=True);
    ASN_title = models.CharField(max_length=50, blank=True, null=True);
    ASN_fax_num = models.IntegerField(blank=True, null=True);
    email_addr = models.CharField(max_length=50, blank=True, null=True);
    
    payment_status = models.CharField(max_length=50, blank=True, null=True);
    amount_received = models.IntegerField(blank=True,null=True)

    anodizing_date = models.DateField(blank=True, null=True);
    anodizing_shift = models.CharField(max_length=50, blank=True, null=True);
    anodizing_load = models.IntegerField(blank=True,null=True);
    anodizing_racked_by = models.CharField(max_length=50, blank=True, null=True);
    anodizing_bar_number = models.IntegerField(blank=True,null=True);
    anodizing_code = models.CharField(max_length=50, blank=True, null=True);
    anodizing_quantity = models.IntegerField(blank=True,null=True);
    anodizing_outside_perimeter = models.FloatField(blank=True, null=True);
    anodizing_length = models.FloatField(blank=True, null=True);
    anodizing_square_feet = models.FloatField(blank=True, null=True);
    
    shipping_date = models.DateField(blank=True, null=True)
    shipping_status = models.CharField(max_length=100, blank=True, null=True)
    shipping_weight = models.FloatField(blank=True, null=True)
    shipping_due = models.FloatField(blank=True,null=True)

    extrusion_completed = models.CharField(max_length=20,null=True);
    shipping_completed = models.CharField(max_length=20,null=True);
    fabrication_completed = models.CharField(max_length=20,null=True);
    anodizing_completed = models.CharField(max_length=20,null=True);
  
    

    
    customer_id = models.ForeignKey(CustomerName, on_delete=models.CASCADE, null=True)
    shipAddress_id = models.ForeignKey(ShipAddress, on_delete=models.CASCADE, null=True)
    billAddress_id = models.ForeignKey(BillAddress, on_delete=models.CASCADE, null=True)
    #line_id = models.ForeignKey(Line, on_delete=models.CASCADE)



class Part(models.Model):
    part_description = models.TextField(blank=True);
    part_number = models.IntegerField(blank=False, null=False);
    active = models.IntegerField(default='1')

    def __str__(self):
        return '(%d) %s' % (self.part_number, self.part_description)

class Account(models.Model):
    account_description = models.TextField(blank=True);
    account_number = models.IntegerField(blank=False, null=False);
    active = models.IntegerField(default='1')

    def __str__(self):
        return '(%d) %s' % (self.account_number, self.account_description)

class Purchase (models.Model):
    requisition_number = models.IntegerField(blank=False, null=True);
    requested_by = models.TextField(blank=True, null=True);
    entry_date = models.DateField(blank=False, null=True);
    project_number = models.IntegerField(blank=True, null=True);
    project_description = models.TextField(blank=True, null=True);
    header_comments = models.TextField(blank=True, null=True);
    line = models.IntegerField(blank=False, null=True);
    quantity = models.IntegerField(blank=True, null=True);
    required_date = models.DateField(blank=False, null=True);
    vendor_one = models.TextField(blank=True, null=True);
    vendor_two = models.TextField(blank=True, null=True);
    vendor_three = models.TextField(blank=True, null=True);
    unit_price_one = models.FloatField(default=False, blank=True, null=True);
    unit_price_two = models.FloatField(default=False, blank=True, null=True);
    unit_price_three = models.FloatField(default=False, blank=True, null=True);
    total = models.FloatField(default=False, blank=True, null=True);
    internal_comments = models.TextField(blank=True, null=True);
    on_hand = models.IntegerField(blank=True, null=True);
    on_order = models.IntegerField(blank=True, null=True);
    reorder_point = models.IntegerField(blank=True, null=True);
    supplier = models.TextField(blank=True, null=True);
    purchase_quantity = models.IntegerField(blank=True, null=True);
    
    requisition_status = models.CharField(max_length=50, null=True);
    purchase_type = models.CharField(max_length=50, null=True);
    red_req = models.CharField(max_length=50, null=True);
    ready_for_approval = models.CharField(max_length=50, null=True);
    approved_yn = models.CharField(max_length=50, null=True);
    buyer = models.CharField(max_length=50, null=True);
    payment_status = models.CharField(max_length=50,blank=True,null=True)
    amount_paid = models.FloatField(blank=True, null=True)
    arrival_status = models.CharField(max_length=100,blank=True,null=True)
    part_id = models.ForeignKey(Part, on_delete=models.CASCADE, null=True)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)

class Manager(models.Model):
    manager = models.TextField()

    def __str__(self):
        return self.manager

class Category(models.Model):
    company = models.TextField()

    def __str__(self):
        return self.company

class SalesReport (models.Model):
    Customerno = models.TextField(blank=True, null=True);
    Companyname = models.TextField(blank=True, null=True);
    Die_Number = models.TextField(blank=True, null=True);
    Invoiceno = models.TextField(blank=True, null=True);
    Salesorderno = models.TextField(blank=True, null=True);
    Lineno_Alt = models.TextField(blank=True, null=True);
    Partno = models.TextField(blank=True, null=True);
    Partdescr = models.TextField(blank=True, null=True);
    Dateshipped = models.DateField(blank=True, null=True);
    Invoicedate = models.DateField(blank=True, null=True);
    Qty_Shipped = models.IntegerField(blank=True, null=True);
    Calc_Actual_Wgt = models.FloatField(default=False, blank=True, null=True);
    Calc_Theor_Wgt = models.FloatField(default=False, blank=True, null=True);
    Calc_Price = models.FloatField(default=False, blank=True, null=True);
    Extrusion_Revenue = models.FloatField(default=False, blank=True, null=True);
    Price_per_Lb = models.FloatField(default=False, blank=True, null=True);
    Fabrication_Lbs = models.FloatField(default=False, blank=True, null=True);
    Fabrication_Revenue = models.FloatField(default=False, blank=True, null=True);
    Paint_Lbs = models.FloatField(default=False, blank=True, null=True);
    Paint_Revenue = models.FloatField(default=False, blank=True, null=True);
    Anodizing_Sq_Ft = models.FloatField(default=False, blank=True, null=True);
    Anodizing_Revenue = models.FloatField(default=False, blank=True, null=True);
    Ingot_Price = models.FloatField(default=False, blank=True, null=True);
    Press = models.CharField(max_length=50, null=True);
    Ordertype = models.CharField(max_length=50, null=True);
    Unitofmeas = models.CharField(max_length=50, null=True);
    Productline = models.CharField(max_length=50, null=True);

    Shiptono = models.TextField(blank=True, null=True);
    Ship_To_State = models.TextField(blank=True, null=True);
    RSM = models.TextField(blank=True, null=True);
    RSM_name = models.TextField(blank=True, null=True);
    
    

class FoundryMaterial (models.Model):
    metal = models.TextField()

    def __str__(self):
        return self.metal

class FoundryLabor (models.Model):
    labor = models.TextField()

    def __str__(self):
        return self.labor

class FoundryOverhead (models.Model):
    overhead = models.TextField()

    def __str__(self):
        return self.overhead

class ExtrusionLabor (models.Model):
    labor = models.TextField()

    def __str__(self):
        return self.labor

class ExtrusionOverhead (models.Model):
    overhead = models.TextField()

    def __str__(self):
        return self.overhead

class FabricationLabor (models.Model):
    labor = models.TextField()

    def __str__(self):
        return self.labor

class FabricationOverhead (models.Model):
    overhead = models.TextField()

    def __str__(self):
        return self.overhead

class AnodizingLabor (models.Model):
    labor = models.TextField()

    def __str__(self):
        return self.labor

class AnodizingOverhead (models.Model):
    overhead = models.TextField()

    def __str__(self):
        return self.overhead

class ShippingLabor (models.Model):
    labor = models.TextField()

    def __str__(self):
        return self.labor

class ShippingOverhead (models.Model):
    overhead = models.TextField()

    def __str__(self):
        return self.overhead

class GeneralReport (models.Model):
    Supplier_Customer_No = models.TextField(blank=True, null=True);
    Name = models.TextField(blank=True, null=True);
    Referenceno = models.TextField(blank=True, null=True);
    Transdate = models.DateField(blank=True, null=True);
    Transamnt = models.FloatField(default=False, blank=True, null=True);
    Transqty = models.IntegerField(blank=True, null=True);
    Period = models.IntegerField(blank=True, null=True);
    Fiscal_Year = models.IntegerField(blank=True, null=True);
    Accountno = models.TextField(blank=True, null=True);
    Type = models.IntegerField(blank=True, null=True);
    Comment_Text = models.TextField(blank=True, null=True);

class General(models.Model):
    gl = models.TextField()

    def __str__(self):
        return self.gl

class Vendor (models.Model):
    vendor = models.TextField()

    def __str__(self):
        return self.vendor

class PurchaseReport (models.Model):
    P_O = models.TextField(blank=True, null=True);
    Vendor_No = models.TextField(blank=True, null=True);
    Vendor_Name = models.TextField(blank=True, null=True);
    line = models.TextField(blank=True, null=True);
    Partno = models.TextField(blank=True, null=True);
    Partdescr = models.TextField(blank=True, null=True);
    GL_Accountno = models.TextField(blank=True, null=True);
    Datepromised = models.DateField(blank=True, null=True);
    Qtyonorder = models.IntegerField(blank=True, null=True);
    Price = models.FloatField(default=False, blank=True, null=True);
    Line_Amount = models.FloatField(default=False, blank=True, null=True);
    Requestedby = models.TextField(blank=True, null=True);
    Buyer = models.TextField(blank=True, null=True);
    Status = models.TextField(blank=True, null=True);
    Projectno = models.TextField(blank=True, null=True);
    Project_Desc = models.TextField(blank=True, null=True);

class Billet(models.Model):
    Date = models.DateField(blank=True, null=True);
    S1_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_7_loose = models.IntegerField(blank=True, null=True, default=0);
    S1_32_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_32_7_loose = models.IntegerField(blank=True, null=True, default=0);
    S1_30_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_30_7_loose = models.IntegerField(blank=True, null=True, default=0);
    S1_28_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_28_7_loose = models.IntegerField(blank=True, null=True, default=0);
    S1_26_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_26_7_loose = models.IntegerField(blank=True, null=True, default=0);
    S1_24_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_24_7_loose = models.IntegerField(blank=True, null=True, default=0);
    S1_22_7_rack = models.IntegerField(blank=True, null=True, default=0);
    S1_22_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_32_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_32_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_31_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_31_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_30_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_30_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_29_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_29_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_28_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_28_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_27_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_27_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_26_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_26_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_24_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_24_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_22_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_22_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_20_7_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_20_7_loose = models.IntegerField(blank=True, null=True, default=0);
    L_24_7_rack = models.IntegerField(blank=True, null=True, default=0);
    L_24_7_loose = models.IntegerField(blank=True, null=True, default=0);
    L_28_7_rack = models.IntegerField(blank=True, null=True, default=0);
    L_28_7_loose = models.IntegerField(blank=True, null=True, default=0);
    L_30_7_rack = models.IntegerField(blank=True, null=True, default=0);
    L_30_7_loose = models.IntegerField(blank=True, null=True, default=0);
    L_32_7_rack = models.IntegerField(blank=True, null=True, default=0);
    L_32_7_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_22_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_22_11_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_24_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_24_11_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_26_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_26_11_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_28_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_28_11_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_30_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_30_11_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_32_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_32_11_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_34_11_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_34_11_loose = models.IntegerField(blank=True, null=True, default=0);
    L_30_11_rack = models.IntegerField(blank=True, null=True, default=0);
    L_30_11_loose = models.IntegerField(blank=True, null=True, default=0);
    L_34_11_rack = models.IntegerField(blank=True, null=True, default=0);
    L_34_11_loose = models.IntegerField(blank=True, null=True, default=0);
    L_32_11_rack = models.IntegerField(blank=True, null=True, default=0);
    L_32_11_loose = models.IntegerField(blank=True, null=True, default=0);
    AP_22_11_rack = models.IntegerField(blank=True, null=True, default=0);
    AP_22_11_loose = models.IntegerField(blank=True, null=True, default=0);
    AP_26_11_rack = models.IntegerField(blank=True, null=True, default=0);
    AP_26_11_loose = models.IntegerField(blank=True, null=True, default=0);
    AP_30_11_rack = models.IntegerField(blank=True, null=True, default=0);
    AP_30_11_loose = models.IntegerField(blank=True, null=True, default=0);
    AP_32_11_rack = models.IntegerField(blank=True, null=True, default=0);
    AP_32_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_34_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_34_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_32_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_32_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_30_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_30_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_28_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_28_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_26_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_26_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_24_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_24_11_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_22_11_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_22_11_loose = models.IntegerField(blank=True, null=True, default=0);
    L_21_14_rack = models.IntegerField(blank=True, null=True, default=0);
    L_21_14_loose = models.IntegerField(blank=True, null=True, default=0);
    A_20_14_rack = models.IntegerField(blank=True, null=True, default=0);
    A_20_14_loose = models.IntegerField(blank=True, null=True, default=0);
    A_22_14_rack = models.IntegerField(blank=True, null=True, default=0);
    A_22_14_loose = models.IntegerField(blank=True, null=True, default=0);
    A_24_14_rack = models.IntegerField(blank=True, null=True, default=0);
    A_24_14_loose = models.IntegerField(blank=True, null=True, default=0);
    A_30_14_rack = models.IntegerField(blank=True, null=True, default=0);
    A_30_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_20_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_20_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_22_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_22_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_24_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_24_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_26_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_26_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_28_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_28_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_30_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_30_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_32_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_32_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_34_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_34_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_36_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_36_14_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_38_14_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_38_14_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_20_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_20_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_22_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_22_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_24_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_24_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_25_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_25_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_26_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_26_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_27_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_27_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_28_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_28_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_29_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_29_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_30_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_30_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_31_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_31_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_32_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_32_9_loose = models.IntegerField(blank=True, null=True, default=0);
    SA_34_9_rack = models.IntegerField(blank=True, null=True, default=0);
    SA_34_9_loose = models.IntegerField(blank=True, null=True, default=0);
    L_32_9_rack = models.IntegerField(blank=True, null=True, default=0);
    L_32_9_loose = models.IntegerField(blank=True, null=True, default=0);
    L_34_9_rack = models.IntegerField(blank=True, null=True, default=0);
    L_34_9_loose = models.IntegerField(blank=True, null=True, default=0);
    L_30_9_rack = models.IntegerField(blank=True, null=True, default=0);
    L_30_9_loose = models.IntegerField(blank=True, null=True, default=0);
    L_22_9_rack = models.IntegerField(blank=True, null=True, default=0);
    L_22_9_loose = models.IntegerField(blank=True, null=True, default=0);
    L_24_9_rack = models.IntegerField(blank=True, null=True, default=0);
    L_24_9_loose = models.IntegerField(blank=True, null=True, default=0);
    L_28_9_rack = models.IntegerField(blank=True, null=True, default=0);
    L_28_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_20_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_20_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_22_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_22_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_24_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_24_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_26_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_26_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_28_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_28_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_30_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_30_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_32_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_32_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_34_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_34_9_loose = models.IntegerField(blank=True, null=True, default=0);
    P1_36_9_rack = models.IntegerField(blank=True, null=True, default=0);
    P1_36_9_loose = models.IntegerField(blank=True, null=True, default=0);
    BB_30_9_rack = models.IntegerField(blank=True, null=True, default=0);
    BB_30_9_loose = models.IntegerField(blank=True, null=True, default=0);
    BB_34_9_rack = models.IntegerField(blank=True, null=True, default=0);
    BB_34_9_loose = models.IntegerField(blank=True, null=True, default=0);
    num_9 = 9;
    num_11 = 11;
    num_20 = 20;
    num_21 = 21;
    num_22 = 22;
    num_23 = 23;
    num_24 = 24;
    num_25 = 25;
    num_26 = 26;
    num_27 = 27;
    num_28 = 28;
    num_29 = 29;
    num_30 = 30;
    num_31 = 31;
    num_32 = 32;
    num_33 = 33;
    num_34 = 34;
    num_35 = 35;
    num_36 = 36;
    num_37 = 37;
    num_38 = 38;
    unit_7 = 3.83;
    unit_11 = 9.22;
    unit_14 = 15.1;
    unit_9 = 6.2;

    @property
    def total_7_weight(self):
        return (self.S1_32_7_rack * self.num_28 + self.S1_32_7_loose)*self.num_32*self.unit_7 +\
               (self.S1_30_7_rack * self.num_28 + self.S1_30_7_loose)*self.num_30*self.unit_7 +\
               (self.S1_28_7_rack * self.num_28 + self.S1_28_7_loose)*self.num_28*self.unit_7 +\
               (self.S1_26_7_rack * self.num_28 + self.S1_26_7_loose)*self.num_26*self.unit_7 +\
               (self.S1_24_7_rack * self.num_28 + self.S1_24_7_loose)*self.num_24*self.unit_7 +\
               (self.S1_22_7_rack * self.num_28 + self.S1_22_7_loose)*self.num_22*self.unit_7 +\
               (self.SA_32_7_rack * self.num_28 + self.SA_32_7_loose)*self.num_32*self.unit_7 +\
               (self.SA_31_7_rack * self.num_28 + self.SA_31_7_loose)*self.num_31*self.unit_7 +\
               (self.SA_30_7_rack * self.num_28 + self.SA_30_7_loose)*self.num_30*self.unit_7 +\
               (self.SA_29_7_rack * self.num_28 + self.SA_29_7_loose)*self.num_29*self.unit_7 +\
               (self.SA_28_7_rack * self.num_28 + self.SA_28_7_loose)*self.num_28*self.unit_7 +\
               (self.SA_27_7_rack * self.num_28 + self.SA_27_7_loose)*self.num_27*self.unit_7 +\
               (self.SA_26_7_rack * self.num_28 + self.SA_26_7_loose)*self.num_26*self.unit_7 +\
               (self.SA_24_7_rack * self.num_28 + self.SA_24_7_loose)*self.num_24*self.unit_7 +\
               (self.SA_22_7_rack * self.num_28 + self.SA_22_7_loose)*self.num_22*self.unit_7 +\
               (self.SA_20_7_rack * self.num_28 + self.SA_20_7_loose)*self.num_20*self.unit_7 +\
               (self.L_24_7_rack * self.num_28 + self.L_24_7_loose)*self.num_24*self.unit_7 +\
               (self.L_28_7_rack * self.num_28 + self.L_28_7_loose)*self.num_28*self.unit_7 +\
               (self.L_30_7_rack * self.num_28 + self.L_30_7_loose)*self.num_30*self.unit_7 +\
               (self.L_32_7_rack * self.num_28 + self.L_32_7_loose)*self.num_32*self.unit_7

    @property
    def total_11_weight(self):
        return (self.SA_22_11_rack * self.num_11 + self.SA_22_11_loose)*self.num_22*self.unit_11 +\
               (self.SA_24_11_rack * self.num_11 + self.SA_24_11_loose)*self.num_24*self.unit_11 +\
               (self.SA_26_11_rack * self.num_11 + self.SA_26_11_loose)*self.num_26*self.unit_11 +\
               (self.SA_28_11_rack * self.num_11 + self.SA_28_11_loose)*self.num_28*self.unit_11 +\
               (self.SA_30_11_rack * self.num_11 + self.SA_30_11_loose)*self.num_30*self.unit_11 +\
               (self.SA_32_11_rack * self.num_11 + self.SA_32_11_loose)*self.num_32*self.unit_11 +\
               (self.SA_34_11_rack * self.num_11 + self.SA_34_11_loose)*self.num_34*self.unit_11 +\
               (self.SA_22_11_rack * self.num_11 + self.SA_22_11_loose)*self.num_22*self.unit_11 +\
               (self.SA_22_11_rack * self.num_11 + self.SA_22_11_loose)*self.num_22*self.unit_11 +\
               (self.L_30_11_rack * self.num_11 + self.L_30_11_loose)*self.num_30*self.unit_11 +\
               (self.L_34_11_rack * self.num_11 + self.L_34_11_loose)*self.num_34*self.unit_11 +\
               (self.L_32_11_rack * self.num_11 + self.L_32_11_loose)*self.num_32*self.unit_11 +\
               (self.AP_22_11_rack * self.num_11 + self.AP_22_11_loose)*self.num_22*self.unit_11 +\
               (self.AP_26_11_rack * self.num_11 + self.AP_26_11_loose)*self.num_26*self.unit_11 +\
               (self.AP_30_11_rack * self.num_11 + self.AP_30_11_loose)*self.num_30*self.unit_11 +\
               (self.AP_32_11_rack * self.num_11 + self.AP_32_11_loose)*self.num_32*self.unit_11 +\
               (self.P1_34_11_rack * self.num_11 + self.P1_34_11_loose)*self.num_34*self.unit_11 +\
               (self.P1_32_11_rack * self.num_11 + self.P1_32_11_loose)*self.num_32*self.unit_11 +\
               (self.P1_30_11_rack * self.num_11 + self.P1_30_11_loose)*self.num_30*self.unit_11 +\
               (self.P1_28_11_rack * self.num_11 + self.P1_28_11_loose)*self.num_28*self.unit_11 +\
               (self.P1_26_11_rack * self.num_11 + self.P1_26_11_loose)*self.num_26*self.unit_11 +\
               (self.P1_24_11_rack * self.num_11 + self.P1_24_11_loose)*self.num_24*self.unit_11 +\
               (self.P1_22_11_rack * self.num_11 + self.P1_22_11_loose)*self.num_22*self.unit_11

    @property
    def total_14_weight(self):
        return (self.L_21_14_rack * self.num_9 + self.L_21_14_loose)*self.num_21*self.unit_14 +\
               (self.A_20_14_rack * self.num_9 + self.A_20_14_loose)*self.num_20*self.unit_14 +\
               (self.A_22_14_rack * self.num_9 + self.A_22_14_loose)*self.num_22*self.unit_14 +\
               (self.A_24_14_rack * self.num_9 + self.A_24_14_loose)*self.num_24*self.unit_14 +\
               (self.A_30_14_rack * self.num_9 + self.A_30_14_loose)*self.num_30*self.unit_14 +\
               (self.P1_20_14_rack * self.num_9 + self.P1_20_14_loose)*self.num_20*self.unit_14 +\
               (self.P1_22_14_rack * self.num_9 + self.P1_22_14_loose)*self.num_22*self.unit_14 +\
               (self.P1_24_14_rack * self.num_9 + self.P1_24_14_loose)*self.num_24*self.unit_14 +\
               (self.P1_26_14_rack * self.num_9 + self.P1_26_14_loose)*self.num_26*self.unit_14 +\
               (self.P1_28_14_rack * self.num_9 + self.P1_28_14_loose)*self.num_28*self.unit_14 +\
               (self.P1_30_14_rack * self.num_9 + self.P1_30_14_loose)*self.num_30*self.unit_14 +\
               (self.P1_32_14_rack * self.num_9 + self.P1_32_14_loose)*self.num_32*self.unit_14 +\
               (self.P1_34_14_rack * self.num_9 + self.P1_34_14_loose)*self.num_34*self.unit_14 +\
               (self.P1_36_14_rack * self.num_9 + self.P1_36_14_loose)*self.num_36*self.unit_14 +\
               (self.P1_38_14_rack * self.num_9 + self.P1_38_14_loose)*self.num_38*self.unit_14

    @property
    def total_9_weight(self):
        return (self.SA_20_9_rack * self.num_20 + self.SA_20_9_loose)*self.num_20*self.unit_9 +\
               (self.SA_22_9_rack * self.num_20 + self.SA_22_9_loose)*self.num_22*self.unit_9 +\
               (self.SA_24_9_rack * self.num_20 + self.SA_24_9_loose)*self.num_24*self.unit_9 +\
               (self.SA_25_9_rack * self.num_20 + self.SA_25_9_loose)*self.num_25*self.unit_9 +\
               (self.SA_26_9_rack * self.num_20 + self.SA_26_9_loose)*self.num_26*self.unit_9 +\
               (self.SA_27_9_rack * self.num_20 + self.SA_27_9_loose)*self.num_27*self.unit_9 +\
               (self.SA_28_9_rack * self.num_20 + self.SA_28_9_loose)*self.num_28*self.unit_9 +\
               (self.SA_29_9_rack * self.num_20 + self.SA_29_9_loose)*self.num_29*self.unit_9 +\
               (self.SA_30_9_rack * self.num_20 + self.SA_30_9_loose)*self.num_30*self.unit_9 +\
               (self.SA_31_9_rack * self.num_20 + self.SA_31_9_loose)*self.num_31*self.unit_9 +\
               (self.SA_32_9_rack * self.num_20 + self.SA_32_9_loose)*self.num_32*self.unit_9 +\
               (self.SA_34_9_rack * self.num_20 + self.SA_34_9_loose)*self.num_34*self.unit_9 +\
               (self.L_32_9_rack * self.num_20 + self.L_32_9_loose)*self.num_32*self.unit_9 +\
               (self.L_34_9_rack * self.num_20 + self.L_34_9_loose)*self.num_34*self.unit_9 +\
               (self.L_30_9_rack * self.num_20 + self.L_30_9_loose)*self.num_30*self.unit_9 +\
               (self.L_22_9_rack * self.num_20 + self.L_22_9_loose)*self.num_22*self.unit_9 +\
               (self.L_24_9_rack * self.num_20 + self.L_24_9_loose)*self.num_24*self.unit_9 +\
               (self.L_28_9_rack * self.num_20 + self.L_28_9_loose)*self.num_28*self.unit_9 +\
               (self.P1_20_9_rack * self.num_20 + self.P1_20_9_loose)*self.num_20*self.unit_9 +\
               (self.P1_22_9_rack * self.num_20 + self.P1_22_9_loose)*self.num_22*self.unit_9 +\
               (self.P1_24_9_rack * self.num_20 + self.P1_24_9_loose)*self.num_24*self.unit_9 +\
               (self.P1_26_9_rack * self.num_20 + self.P1_26_9_loose)*self.num_26*self.unit_9 +\
               (self.P1_28_9_rack * self.num_20 + self.P1_28_9_loose)*self.num_28*self.unit_9 +\
               (self.P1_30_9_rack * self.num_20 + self.P1_30_9_loose)*self.num_30*self.unit_9 +\
               (self.P1_32_9_rack * self.num_20 + self.P1_32_9_loose)*self.num_32*self.unit_9 +\
               (self.P1_34_9_rack * self.num_20 + self.P1_34_9_loose)*self.num_34*self.unit_9 +\
               (self.P1_36_9_rack * self.num_20 + self.P1_36_9_loose)*self.num_36*self.unit_9 +\
               (self.BB_30_9_rack * self.num_20 + self.BB_30_9_loose)*self.num_30*self.unit_9 +\
               (self.BB_34_9_rack * self.num_20 + self.BB_34_9_loose)*self.num_34*self.unit_9

    @property
    def total_billet(self):
        return self.total_7_weight + self.total_9_weight + self.total_11_weight + self.total_14_weight

class Log(models.Model):
    Date = models.DateField(blank=True, null=True);
    Cropped_S1_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_S1_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_S1_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_S1_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_S1_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_S1_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_SA_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_SA_7_len2 = models.FloatField(default=0,  blank=True, null=True);
    Cropped_SA_7_len3 = models.FloatField(default=0,  blank=True, null=True);
    Cropped_SA_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_SA_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_SA_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_L_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_L_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_L_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_L_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_L_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_L_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_BB_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_BB_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_BB_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_BB_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_BB_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_BB_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_1350_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_1350_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_1350_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_1350_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_1350_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_1350_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_other_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_other_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_other_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_other_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_other_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_other_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_BB_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_BB_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_BB_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_BB_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_BB_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_BB_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_SA_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_SA_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_SA_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_SA_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_SA_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_SA_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_S1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_S1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_S1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_S1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_S1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_S1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_P1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_P1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_P1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_P1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_P1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_P1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_L_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_L_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_L_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_L_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_L_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_L_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_M_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Cropped_M_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Cropped_M_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Cropped_M_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_M_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Cropped_M_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_S1_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_S1_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_S1_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_S1_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_S1_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_S1_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_6005A_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_6005A_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_6005A_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_6005A_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_6005A_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_6005A_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_9_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_9_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_9_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_9_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_9_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_9_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_9_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_9_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_9_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_9_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_9_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_9_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_9_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_9_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_9_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_9_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_9_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_9_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_AP_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_AP_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_AP_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_AP_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_AP_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_AP_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_M1_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_M1_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_M1_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_M1_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_M1_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_M1_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_L_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_L_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_M1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_M1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_M1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_M1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_M1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_M1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_BB_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_BB_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_BB_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_BB_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_BB_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_BB_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_SA_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_SA_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_S1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_S1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_S1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_S1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_S1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_S1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Homo_P1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Homo_P1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_S1_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_S1_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_S1_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_S1_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_S1_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_S1_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_6005A_7_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_6005A_7_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_6005A_7_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_6005A_7_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_6005A_7_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_6005A_7_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_9_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_9_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_9_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_9_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_9_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_9_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_9_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_9_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_9_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_9_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_9_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_9_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_9_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_9_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_9_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_9_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_9_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_9_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_AP_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_AP_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_AP_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_AP_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_AP_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_AP_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_M1_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_M1_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_M1_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_M1_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_M1_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_M1_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_11_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_11_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_11_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_11_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_11_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_11_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_L_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_L_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_M1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_M1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_M1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_M1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_M1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_M1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_BB_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_BB_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_BB_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_BB_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_BB_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_BB_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_SA_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_SA_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_S1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_S1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_S1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_S1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_S1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_S1_16_num3 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_16_len1 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_16_len2 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_16_len3 = models.FloatField(default=0, blank=True, null=True);
    Unhomo_P1_16_num1 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_16_num2 = models.IntegerField(default=0, blank=True, null=True);
    Unhomo_P1_16_num3 = models.IntegerField(default=0, blank=True, null=True);

    @property
    def cropped_log(self):
        return (self.Cropped_S1_7_len1 * self.Cropped_S1_7_num1 + self.Cropped_S1_7_len2 * self.Cropped_S1_7_num2 + self.Cropped_S1_7_len3 * self.Cropped_S1_7_num3)*3.83 +\
               (self.Cropped_SA_7_len1 * self.Cropped_SA_7_num1 + self.Cropped_SA_7_len2 * self.Cropped_SA_7_num2 + self.Cropped_SA_7_len3 * self.Cropped_SA_7_num3)*3.83 +\
               (self.Cropped_L_7_len1 * self.Cropped_L_7_num1 + self.Cropped_L_7_len2 * self.Cropped_L_7_num2 + self.Cropped_L_7_len3 * self.Cropped_L_7_num3)*3.83 +\
               (self.Cropped_BB_7_len1 * self.Cropped_BB_7_num1 + self.Cropped_BB_7_len2 * self.Cropped_BB_7_num2 + self.Cropped_BB_7_len3 * self.Cropped_BB_7_num3)*3.83 +\
               (self.Cropped_1350_7_len1 * self.Cropped_1350_7_num1 + self.Cropped_1350_7_len2 * self.Cropped_1350_7_num2 + self.Cropped_1350_7_len3 * self.Cropped_1350_7_num3)*3.83 +\
               (self.Cropped_other_7_len1 * self.Cropped_other_7_num1 + self.Cropped_other_7_len2 * self.Cropped_other_7_num2 + self.Cropped_other_7_len3 * self.Cropped_other_7_num3)*3.83 +\
               (self.Cropped_BB_16_len1 * self.Cropped_BB_16_num1 + self.Cropped_BB_16_len2 * self.Cropped_BB_16_num2 + self.Cropped_BB_16_len3 * self.Cropped_BB_16_num3)*19.72 +\
               (self.Cropped_SA_16_len1 * self.Cropped_SA_16_num1 + self.Cropped_SA_16_len2 * self.Cropped_SA_16_num2 + self.Cropped_SA_16_len3 * self.Cropped_SA_16_num3)*19.72 +\
               (self.Cropped_S1_16_len1 * self.Cropped_S1_16_num1 + self.Cropped_S1_16_len2 * self.Cropped_S1_16_num2 + self.Cropped_S1_16_len3 * self.Cropped_S1_16_num3)*19.72 +\
               (self.Cropped_P1_16_len1 * self.Cropped_P1_16_num1 + self.Cropped_P1_16_len2 * self.Cropped_P1_16_num2 + self.Cropped_P1_16_len3 * self.Cropped_P1_16_num3)*19.72 +\
               (self.Cropped_L_16_len1 * self.Cropped_L_16_num1 + self.Cropped_L_16_len2 * self.Cropped_L_16_num2 + self.Cropped_L_16_len3 * self.Cropped_L_16_num3)*19.72 +\
               (self.Cropped_M_16_len1 * self.Cropped_M_16_num1 + self.Cropped_M_16_len2 * self.Cropped_M_16_num2 + self.Cropped_M_16_len3 * self.Cropped_M_16_num3)*19.72

    @property
    def homo_log(self):
        return (self.Homo_S1_7_len1 * self.Homo_S1_7_num1 + self.Homo_S1_7_len2 * self.Homo_S1_7_num2 + self.Homo_S1_7_len3 * self.Homo_S1_7_num3)*3.83 +\
               (self.Homo_SA_7_len1 * self.Homo_SA_7_num1 + self.Homo_SA_7_len2 * self.Homo_SA_7_num2 + self.Homo_SA_7_len3 * self.Homo_SA_7_num3)*3.83 +\
               (self.Homo_6005A_7_len1 * self.Homo_6005A_7_num1 + self.Homo_6005A_7_len2 * self.Homo_6005A_7_num2 + self.Homo_6005A_7_len3 * self.Homo_6005A_7_num3)*3.83 +\
               (self.Homo_P1_9_len1 * self.Homo_P1_9_num1 + self.Homo_P1_9_len2 * self.Homo_P1_9_num2 + self.Homo_P1_9_len3 * self.Homo_P1_9_num3)*6.2 +\
               (self.Homo_SA_9_len1 * self.Homo_SA_9_num1 + self.Homo_SA_9_len2 * self.Homo_SA_9_num2 + self.Homo_SA_9_len3 * self.Homo_SA_9_num3)*6.2 +\
               (self.Homo_L_9_len1 * self.Homo_L_9_num1 + self.Homo_L_9_len2 * self.Homo_L_9_num2 + self.Homo_L_9_len3 * self.Homo_L_9_num3)*6.2 +\
               (self.Homo_L_11_len1 * self.Homo_L_11_num1 + self.Homo_L_11_len2 * self.Homo_L_11_num2 + self.Homo_L_11_len3 * self.Homo_L_11_num3)*9.22 +\
               (self.Homo_SA_11_len1 * self.Homo_SA_11_num1 + self.Homo_SA_11_len2 * self.Homo_SA_11_num2 + self.Homo_SA_11_len3 * self.Homo_SA_11_num3)*9.22 +\
               (self.Homo_AP_11_len1 * self.Homo_AP_11_num1 + self.Homo_AP_11_len2 * self.Homo_AP_11_num2 + self.Homo_AP_11_len3 * self.Homo_AP_11_num3)*9.22 +\
               (self.Homo_M1_11_len1 * self.Homo_M1_11_num1 + self.Homo_M1_11_len2 * self.Homo_M1_11_num2 + self.Homo_M1_11_len3 * self.Homo_M1_11_num3)*9.22 +\
               (self.Homo_P1_11_len1 * self.Homo_P1_11_num1 + self.Homo_P1_11_len2 * self.Homo_P1_11_num2 + self.Homo_P1_11_len3 * self.Homo_P1_11_num3)*9.22 +\
               (self.Homo_L_16_len1 * self.Homo_L_16_num1 + self.Homo_L_16_len2 * self.Homo_L_16_num2 + self.Homo_L_16_len3 * self.Homo_L_16_num3)*19.72 +\
               (self.Homo_M1_16_len1 * self.Homo_M1_16_num1 + self.Homo_M1_16_len2 * self.Homo_M1_16_num2 + self.Homo_M1_16_len3 * self.Homo_M1_16_num3)*19.72 +\
               (self.Homo_BB_16_len1 * self.Homo_BB_16_num1 + self.Homo_BB_16_len2 * self.Homo_BB_16_num2 + self.Homo_BB_16_len3 * self.Homo_BB_16_num3)*19.72 +\
               (self.Homo_SA_16_len1 * self.Homo_SA_16_num1 + self.Homo_SA_16_len2 * self.Homo_SA_16_num2 + self.Homo_SA_16_len3 * self.Homo_SA_16_num3)*19.72 +\
               (self.Homo_S1_16_len1 * self.Homo_S1_16_num1 + self.Homo_S1_16_len2 * self.Homo_S1_16_num2 + self.Homo_S1_16_len3 * self.Homo_S1_16_num3)*19.72 +\
               (self.Homo_P1_16_len1 * self.Homo_P1_16_num1 + self.Homo_P1_16_len2 * self.Homo_P1_16_num2 + self.Homo_P1_16_len3 * self.Homo_P1_16_num3)*19.72
    @property
    def unhomo_log(self):
        return (self.Unhomo_S1_7_len1 * self.Unhomo_S1_7_num1 + self.Unhomo_S1_7_len2 * self.Unhomo_S1_7_num2 + self.Unhomo_S1_7_len3 * self.Unhomo_S1_7_num3)*3.83 +\
               (self.Unhomo_SA_7_len1 * self.Unhomo_SA_7_num1 + self.Unhomo_SA_7_len2 * self.Unhomo_SA_7_num2 + self.Unhomo_SA_7_len3 * self.Unhomo_SA_7_num3)*3.83 +\
               (self.Unhomo_6005A_7_len1 * self.Unhomo_6005A_7_num1 + self.Unhomo_6005A_7_len2 * self.Unhomo_6005A_7_num2 + self.Unhomo_6005A_7_len3 * self.Unhomo_6005A_7_num3)*3.83 +\
               (self.Unhomo_P1_9_len1 * self.Unhomo_P1_9_num1 + self.Unhomo_P1_9_len2 * self.Unhomo_P1_9_num2 + self.Unhomo_P1_9_len3 * self.Unhomo_P1_9_num3)*6.2 +\
               (self.Unhomo_SA_9_len1 * self.Unhomo_SA_9_num1 + self.Unhomo_SA_9_len2 * self.Unhomo_SA_9_num2 + self.Unhomo_SA_9_len3 * self.Unhomo_SA_9_num3)*6.2 +\
               (self.Unhomo_L_9_len1 * self.Unhomo_L_9_num1 + self.Unhomo_L_9_len2 * self.Unhomo_L_9_num2 + self.Unhomo_L_9_len3 * self.Unhomo_L_9_num3)*6.2 +\
               (self.Unhomo_L_11_len1 * self.Unhomo_L_11_num1 + self.Unhomo_L_11_len2 * self.Unhomo_L_11_num2 + self.Unhomo_L_11_len3 * self.Unhomo_L_11_num3)*9.22 +\
               (self.Unhomo_SA_11_len1 * self.Unhomo_SA_11_num1 + self.Unhomo_SA_11_len2 * self.Unhomo_SA_11_num2 + self.Unhomo_SA_11_len3 * self.Unhomo_SA_11_num3)*9.22 +\
               (self.Unhomo_AP_11_len1 * self.Unhomo_AP_11_num1 + self.Unhomo_AP_11_len2 * self.Unhomo_AP_11_num2 + self.Unhomo_AP_11_len3 * self.Unhomo_AP_11_num3)*9.22 +\
               (self.Unhomo_M1_11_len1 * self.Unhomo_M1_11_num1 + self.Unhomo_M1_11_len2 * self.Unhomo_M1_11_num2 + self.Unhomo_M1_11_len3 * self.Unhomo_M1_11_num3)*9.22 +\
               (self.Unhomo_P1_11_len1 * self.Unhomo_P1_11_num1 + self.Unhomo_P1_11_len2 * self.Unhomo_P1_11_num2 + self.Unhomo_P1_11_len3 * self.Unhomo_P1_11_num3)*9.22 +\
               (self.Unhomo_L_16_len1 * self.Unhomo_L_16_num1 + self.Unhomo_L_16_len2 * self.Unhomo_L_16_num2 + self.Unhomo_L_16_len3 * self.Unhomo_L_16_num3)*19.72 +\
               (self.Unhomo_M1_16_len1 * self.Unhomo_M1_16_num1 + self.Unhomo_M1_16_len2 * self.Unhomo_M1_16_num2 + self.Unhomo_M1_16_len3 * self.Unhomo_M1_16_num3)*19.72 +\
               (self.Unhomo_BB_16_len1 * self.Unhomo_BB_16_num1 + self.Unhomo_BB_16_len2 * self.Unhomo_BB_16_num2 + self.Unhomo_BB_16_len3 * self.Unhomo_BB_16_num3)*19.72 +\
               (self.Unhomo_SA_16_len1 * self.Unhomo_SA_16_num1 + self.Unhomo_SA_16_len2 * self.Unhomo_SA_16_num2 + self.Unhomo_SA_16_len3 * self.Unhomo_SA_16_num3)*19.72 +\
               (self.Unhomo_S1_16_len1 * self.Unhomo_S1_16_num1 + self.Unhomo_S1_16_len2 * self.Unhomo_S1_16_num2 + self.Unhomo_S1_16_len3 * self.Unhomo_S1_16_num3)*19.72 +\
               (self.Unhomo_P1_16_len1 * self.Unhomo_P1_16_num1 + self.Unhomo_P1_16_len2 * self.Unhomo_P1_16_num2 + self.Unhomo_P1_16_len3 * self.Unhomo_P1_16_num3)*19.72
    @property
    def total_log(self):
        return self.cropped_log + self.homo_log + self.unhomo_log
      
class SalesMonthly(models.Model):
    month = models.IntegerField()
    seventeen = models.FloatField()
    eighteen = models.FloatField()
    nineteen = models.FloatField()

class PurchaseMonthly(models.Model):
    month = models.IntegerField()
    seventeen = models.FloatField()
    eighteen = models.FloatField()
    nineteen = models.FloatField()

class SalesCustomer(models.Model):
    month = models.IntegerField()
    top1 = models.FloatField()
    top2 = models.FloatField()
    top3 = models.FloatField()

class PurchaseVendor(models.Model):
    month = models.IntegerField()
    top1 = models.FloatField()
    top2 = models.FloatField()
    top3 = models.FloatField()

class SalesManager(models.Model):
    month = models.IntegerField()
    top1 = models.FloatField()
    top2 = models.FloatField()
    top3 = models.FloatField()

class PurchaseDepartment(models.Model):
    month = models.IntegerField()
    top1 = models.FloatField()
    top2 = models.FloatField()
    top3 = models.FloatField()

class Revenue(models.Model):
    date = models.DateField(blank=True, null=True);
    revenue = models.FloatField(default=False, blank=True, null=True);



class Foundry(models.Model):
    date = models.DateField(blank=True, null=True);
    furnace_number = models.IntegerField(blank=True, null=True);
    heat_number = models.IntegerField(blank=True, null=True);
    length = models.IntegerField(blank=True, null=True);
    diameter = models.IntegerField(blank=True, null=True);
    alloy = models.IntegerField(blank=True, null=True);
    cast_qty = models.IntegerField(blank=True, null=True);
    total_weight = models.FloatField(default=0, blank=True, null=True);
    degass = models.IntegerField(blank=True, null=True);
    cast_shift = models.CharField(max_length=50, null=True);
    cast_speed = models.IntegerField(blank=True, null=True);
    Mg = models.FloatField(default=0, blank=True, null=True);
    Si = models.FloatField(default=0, blank=True, null=True);
    Fe = models.FloatField(default=0, blank=True, null=True);
    Cu = models.FloatField(default=0, blank=True, null=True);
    Cr = models.FloatField(default=0, blank=True, null=True);
    Mn = models.FloatField(default=0, blank=True, null=True);
    Zn = models.FloatField(default=0, blank=True, null=True);
    Ti = models.FloatField(default=0, blank=True, null=True);
    Bo = models.FloatField(default=0, blank=True, null=True);
    
    Mg_HL = models.CharField(max_length=50, null=True);
    Si_HL = models.CharField(max_length=50, null=True);
    Fe_HL = models.CharField(max_length=50, null=True);
    Cu_HL = models.CharField(max_length=50, null=True);
    Cr_HL = models.CharField(max_length=50, null=True);
    Mn_HL = models.CharField(max_length=50, null=True);
    Zn_HL = models.CharField(max_length=50, null=True);
    Ti_HL = models.CharField(max_length=50, null=True);
    Bo_HL = models.CharField(max_length=50, null=True);

'''    
class Extrusion(models.Model):
    date = models.DateField(blank=True, null=True);
    press_code = models.CharField(max_length=50, null=True);
    shift_code = models.CharField(max_length=50, null=True);
    maint_down_time = models.FloatField(default=0, blank=True, null=True);
    other_down_time = models.FloatField(default=0, blank=True, null=True);
    headcount = models.IntegerField(blank=True, null=True);
    net_lbs_extruded = models.FloatField(default=0, blank=True, null=True);
    gross_lbs_extruded = models.FloatField(default=0, blank=True, null=True);
    percent_attainment = models.FloatField(default=0, blank=True, null=True);
    safety_comments = models.TextField(blank=True, null=False);
    overrun_comments = models.TextField(blank=True, null=False);
    out_of_tolerance_comments = models.TextField(blank=True, null=False);
    surface_defects_comments = models.TextField(blank=True, null=False);
    cooling_defects_comments = models.TextField(blank=True, null=False);
    handling_defects_comments = models.TextField(blank=True, null=False);
    attempted_die_runs = models.IntegerField(blank=True, null=True);
    successful_die_runs = models.IntegerField(blank=True, null=True);
    plugged_run = models.IntegerField(blank=True, null=True);
    dimensional_run = models.IntegerField(blank=True, null=True);
    finished_run = models.IntegerField(blank=True, null=True);
    broken_run = models.IntegerField(blank=True, null=True);
    run_attainment_percent = models.FloatField(default=0, blank=True, null=True);
'''

class Maintenance(models.Model):
    date = models.DateField(null=True);
    department = models.CharField(max_length=100, null=True)
    hours = models.FloatField(null=True)
    comment = models.TextField(null=True)

class Capitalinjection(models.Model):
    date = models.DateField(null=True)
    capital_injection_amount = models.FloatField(null=True)
    capital_injection_comment = models.TextField(null=True)


name =[("sales_order_entry","Sales Order Entry"),("purchase_order_entry","Purchase Order entry"),("revenue_entry","Revenue Entry"),("inventory_entry","Inventory Entry"),("foundry_data_entry","Foundry Data Entry"),("extrusion_data_entry","Extrusion Data Entry")]
role = [('manager','Manager'),('employee','Employee')]
department = models.CharField(max_length=255, choices=name,null=True)
position   = models.CharField(max_length=255,choices=role,null=True)
department.contribute_to_class(User, 'department')
position.contribute_to_class(User, 'position')
