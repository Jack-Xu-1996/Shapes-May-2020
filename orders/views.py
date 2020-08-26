from django.shortcuts import render, redirect
from .models import Order, Line, Price, CustomerName, BillAddress, ShipAddress, Part, Account, Purchase, SalesReport, PurchaseReport, Category, Manager, Vendor, General,\
     PurchaseMonthly, SalesMonthly, SalesCustomer, PurchaseVendor, SalesManager, PurchaseDepartment, GeneralReport,\
     FoundryMaterial, FoundryLabor, FoundryOverhead, ExtrusionLabor, ExtrusionOverhead, FabricationLabor, FabricationOverhead, AnodizingLabor, AnodizingOverhead, ShippingLabor, ShippingOverhead,\
     Billet, Log,\
     Revenue,Foundry, Maintenance,Capitalinjection
from .forms import OrderForm
from .formsPurchase import PurchaseForm
from .formsLine import OrderLine
from .formsAddress import BillAddressForm, ShipAddressForm, CustomerNameForm
from .formsPart import PartForm
from .formsAccount import AccountForm
from .formsPrice import PriceForm
from .formsReportsales import SalesreportForm
from .formsReportpurchase import PurchasereportForm
from .formsBillet import BilletForm
from .formsLog import LogForm
from .formsRevenue import RevenueForm
from .formsFoundry import FoundryForm
from .formsMaintenance import MaintenanceForm
from .formsinjection import CapitalinjectionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart
from django.db.models import Avg, Sum, Count, Min, Max, Q
from django.db.models.functions import TruncMonth

import openpyxl, xlrd
from datetime import datetime, timedelta
from django.db.models import F, Func
from django.contrib.auth.models import User
import random 
from django.http import HttpResponse
from django.contrib.humanize.templatetags.humanize import intcomma
import json


class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 2)'

def get_value(user_id):
    staff = User.objects.filter(id=user_id,is_staff=True)
    if staff:
        admin_user = True
        department = None
        position   = None
    else:
        all_value = User.objects.filter(id=user_id,is_active=True).values()
        department = all_value[0].get('department')
        position =  all_value[0].get('position')
        admin_user = False
    data = {'admin_user':admin_user,'department':department,'position':position}
    return data

@login_required
def index_chart(request):
    response = get_value(request.user.id)
    enddate = datetime.today()
    startdate = enddate - timedelta(days=30)
    log = Log.objects.all().order_by('-Date')
    billet = Billet.objects.all().order_by('-Date')

    #Inventory Chart
    if not log and not billet:
        inventory_chart = [['7" billet',random.randint(1,100)],['9" billet',random.randint(1,100)],['11" billet',random.randint(1,100)],['14" billet',random.randint(1,100)],['cropped log',random.randint(1,100)],['homogenized log',random.randint(1,100)],['unhomogenized log',random.randint(1,100)]]
    else:
        li=[]
        for i in billet:
            li.append(['7" billet',i.total_7_weight])
            li.append(['9" billet',i.total_11_weight])
            li.append(['11" billet',i.total_14_weight])
            li.append(['14" billet',i.total_9_weight])
            break
        for i in log:
            li.append(['cropped log',i.cropped_log])
            li.append(['homogenized log',i.homo_log])
            li.append(['unhomogenized log',i.unhomo_log])
            break;
        inventory_chart = li


    #Shipping Due Chart

    shipping_data = Order.objects.all().values('id','shipping_due','shipping_weight')
    shipping_due_list = []
    shipping_weigth_list= []
    dictionary_form={}
    d=[]
    for i in shipping_data:
        shipping_due=i.get('shipping_due')
        shipping_weight=i.get('shipping_weight')
        shipping_due = shipping_due if shipping_due  else 0.0
        shipping_weight = shipping_weight if shipping_weight  else 0.0
        dictionary_form[shipping_due] = [shipping_weight,float(shipping_due)-float(shipping_weight),shipping_due,i.get('id')]
    sorted_value={k: v for k, v in sorted(dictionary_form.items(), key=lambda item: item[0])}
    top_three_list=list(sorted_value.values())[-3:]
    if len(top_three_list) == 3:
        three = top_three_list[2]
        two = top_three_list[1]
        one = top_three_list[0]
    else:
        three = [12.0,4.0,16.0]
        two =  [10.0,2.0,12.0]
        one = [8.0,5.0,13.0]

    #Receiving Payment Chart    
    recent_receive = Order.objects.filter(required_date__range=[startdate, enddate]).values('required_date').annotate(total=Round(Sum('amount_received'))).order_by()
    recent_payment = Purchase.objects.filter(required_date__range=[startdate, enddate]).values('required_date').annotate(total=Round(Sum('total'))).order_by()
    print(recent_receive)
    print(recent_payment)
    recent_customer =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_receive},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'required_date': 'required_date',
                'sales': 'total'}]
                },

       
             ])
    cht16 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'required_date': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Cash available of Past 30 days - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Date'}},
               'yAxis': {
                   'title': {'text': 'Cash Available'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    return render(request, 'indexchart.html', {'chart_list': [cht16],'inventory_chart':inventory_chart,'response':response,'three':three,'two':two,'one':one})

@login_required
def index(request):
    orders = Order.objects.all()
    response = get_value(request.user.id)
    department = response.get('department')
    # if department == 'purchase_order_entry':
    #     return redirect('/purchase')
    # elif department == 'inventory_entry':
    #     return redirect('/order/indexlog/')
    # elif department == 'revenue_entry':
    #     return redirect('/order/indexrevenue/')
    # elif department == 'foundry_data_entry':
    #     return redirect('/order/indexfoundry/')
    # elif department == 'extrusion_data_entry':
    #     return redirect('/order/indexextrusion/')
    
    return render(request, 'index.html', {'orders': orders,'response':response})

@login_required
def indexline(request):
    lines = Line.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexline.html', {'lines': lines,'response':response})

@login_required
def indexprice(request):
    prices = Price.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexprice.html', {'prices': prices,'response':response})

@login_required
def index_sales_report(request):
    sales = SalesReport.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexsalesreport.html', {'sales': sales,'response':response})

@login_required
def index_purchase_report(request):
    purchase = PurchaseReport.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexpurchasereport.html', {'purchase': purchase,'response':response})

@login_required
def destroy_sales_report(request):
    SalesReport.objects.all().delete()
    return redirect('/order/indexsalesreport', messages.success(request, 'Sales Report was successfully deleted.', 'alert-success'))

@login_required
def destroy_purchase_report(request):
    PurchaseReport.objects.all().delete()
    return redirect('/order/indexpurchasereport', messages.success(request, 'Purchase Report was successfully deleted.', 'alert-success'))

#start customize sales chart customer

def is_valid_queryparam(param):
    return param != '' and param is not None



def filter(request):

  
    qs = SalesReport.objects.filter(Calc_Price__gt=0).order_by('Invoicedate')
    categories = Category.objects.all()
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam(date_min):
        qs = qs.filter(Invoicedate__gte=date_min)

    if is_valid_queryparam(date_max):
        qs = qs.filter(Invoicedate__lt=date_max)

    if is_valid_queryparam(category) and category != 'Choose...':
        qs = qs.filter(Companyname=category)
   
    return qs

def test(request):
  qs = filter(request)

def infinite_filter(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    return SalesReport.objects.filter(Calc_Price__gt=0)[int(offset): int(offset) + int(limit)]


def is_there_more_data(request):
    offset = request.GET.get('offset')
    if int(offset) > SalesReport.objects.filter(Calc_Price__gt=0).count():
        return False
    return True


def BootstrapFilterView(request):
    #qs = filter(request)
    response = get_value(request.user.id)
    context = {
        
        'categories': Category.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form.html", context)

#end customize sales chart customer

#start customize sales chart manager
def performance(request):
    import datetime
    t1 = datetime.datetime.now()
    chart_data = []
    chart_date = []
    data = []
    s_data={}
    from django.http import JsonResponse

    qs = SalesReport.objects.filter(Calc_Price__gt=0).order_by('Invoicedate')
    categories = Category.objects.all()
    date_min = request.GET.get('json_response[date_min]')
    date_max = request.GET.get('json_response[date_max]')
    category = request.GET.get('json_response[category]')
    page = request.GET.get('json_response[page]')
    if is_valid_queryparam(date_min):
        qs = qs.filter(Invoicedate__gte=date_min)
    if is_valid_queryparam(date_max):
        qs = qs.filter(Invoicedate__lt=date_max) 

    if is_valid_queryparam(category) and category != 'Choose...':
        if page == 'company_name':
            qs = qs.filter(Companyname=category)
        elif page == 'RSM_name':
            qs = qs.filter(RSM_name=category)


    for i in qs:
        
        journal_id = i.id
        Invoicedate = i.Invoicedate.strftime("%B %d, %Y")
        chart_date_value = i.Invoicedate.strftime('%Y-%m-%d')
        if page == 'company_name':
            company_name = i.Companyname
        elif page =='RSM_name':
            company_name = i.RSM_name
        dollars = i.Calc_Price
        print(dollars)
        dollars = round(float(dollars), 2)
        s3="$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
        Calc_Price = s3
        buttons= '<a href="/order/checksales/'+str(i.id)+'" class="btn ink-reaction btn-floating-action btn-info"><i class="md md-search"></i> </a>'
        table_data = [journal_id,Invoicedate,company_name,Calc_Price,buttons]
        chart_data_format = [chart_date_value,dollars]
        chart_data.append(chart_data_format)
        chart_date.append(chart_date_value)
        data.append(table_data)
    s_data['data'] = data
    s_data['chart_data'] = chart_data
    s_data['chart_date'] = chart_date
    t2 = datetime.datetime.now()
    print(t2 - t1)

    return JsonResponse(s_data)



def is_valid_queryparam_sales3(param):
    return param != '' and param is not None



def filter_sales3(request):

  
    qs = SalesReport.objects.filter(Calc_Price__gt=0).order_by('Invoicedate')
    categories = Manager.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_sales3(date_min):
        qs = qs.filter(Invoicedate__gte=date_min)

    if is_valid_queryparam_sales3(date_max):
        qs = qs.filter(Invoicedate__lt=date_max)

    if is_valid_queryparam_sales3(category) and category != 'Choose...':
        qs = qs.filter(RSM_name=category)
   
    return qs


def infinite_filter_sales3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    return SalesReport.objects.filter(Calc_Price__gt=0)[int(offset): int(offset) + int(limit)]


def is_there_more_data_sales3(request):
    offset = request.GET.get('offset')
    if int(offset) > SalesReport.objects.filter(Calc_Price__gt=0).count():
        return False
    return True


def BootstrapFilterView_sales3(request):
    #qs = filter_sales3(request)
    response = get_value(request.user.id)
    context = {
        # 'queryset': qs,
        'categories': Manager.objects.all(),
        'response':response
    }
   
    return render(request, "bootstrap_form_sales3.html", context)

#end customize sales chart customer

#start customize purchase chart vendor

def is_valid_queryparam_purchase2(param):
    return param != '' and param is not None


def filter_purchase2(request):
    qs = PurchaseReport.objects.filter(Line_Amount__gt=0).order_by('Datepromised')
    categories = Vendor.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_purchase2(date_min):
        qs = qs.filter(Datepromised__gte=date_min)

    if is_valid_queryparam_purchase2(date_max):
        qs = qs.filter(Datepromised__lt=date_max)

    if is_valid_queryparam_purchase2(category) and category != 'Choose...':
        qs = qs.filter(Vendor_Name=category)

    return qs


def infinite_filter_purchase2(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    return PurchaseReport.objects.filter(Line_Amount__gt=0)[int(offset): int(offset) + int(limit)]


def is_there_more_data_purchase2(request):
    offset = request.GET.get('offset')
    if int(offset) > PurchaseReport.objects.filter(Line_Amount__gt=0).count():
        return False
    return True


def BootstrapFilterView_purchase2(request):
    qs = filter_purchase2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': Vendor.objects.all(),
        'response':response
    }
    
   
    return render(request, "bootstrap_form_purchase2.html", context)

#end customize purchase chart vendor

#start customize purchase chart gl

def is_valid_queryparam_purchase3(param):
    return param != '' and param is not None


def filter_purchase3(request):
    qs = PurchaseReport.objects.filter(Line_Amount__gt=0).order_by('Datepromised')
    categories = General.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_purchase3(date_min):
        qs = qs.filter(Datepromised__gte=date_min)

    if is_valid_queryparam_purchase3(date_max):
        qs = qs.filter(Datepromised__lt=date_max)

    if is_valid_queryparam_purchase3(category) and category != 'Choose...':
        qs = qs.filter(GL_Accountno=category)

    return qs


def infinite_filter_purchase3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    return PurchaseReport.objects.filter(Line_Amount__gt=0)[int(offset): int(offset) + int(limit)]


def is_there_more_data_purchase3(request):
    offset = request.GET.get('offset')
    if int(offset) > PurchaseReport.objects.filter(Line_Amount__gt=0).count():
        return False
    return True


def BootstrapFilterView_purchase3(request):
    qs = filter_purchase3(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': General.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_purchase3.html", context)

#end customize purchase chart gl


#start customize foundry chart metal

def is_valid_queryparam_foundry1(param):
    return param != '' and param is not None


def filter_foundry1(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_metal = summary_initial.filter(Accountno=5100717) | summary_initial.filter(Accountno=5100726) |\
                             summary_initial.filter(Accountno=5100716) | summary_initial.filter(Accountno=5100710) |\
                             summary_initial.filter(Accountno=5100715) | summary_initial.filter(Accountno=5100720) |\
                             summary_initial.filter(Accountno=5100719) | summary_initial.filter(Accountno=5100714) |\
                             summary_initial.filter(Accountno=5100711) | summary_initial.filter(Accountno=5100707) |\
                             summary_initial.filter(Accountno=5100712) | summary_initial.filter(Accountno=5100718)
    qs = summary_foundry_metal.order_by('Transdate')
    categories = FoundryMaterial.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_foundry1(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_foundry1(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_foundry1(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_foundry1(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_metal = summary_initial.filter(Accountno=5100717) | summary_initial.filter(Accountno=5100726) |\
                             summary_initial.filter(Accountno=5100716) | summary_initial.filter(Accountno=5100710) |\
                             summary_initial.filter(Accountno=5100715) | summary_initial.filter(Accountno=5100720) |\
                             summary_initial.filter(Accountno=5100719) | summary_initial.filter(Accountno=5100714) |\
                             summary_initial.filter(Accountno=5100711) | summary_initial.filter(Accountno=5100707) |\
                             summary_initial.filter(Accountno=5100712) | summary_initial.filter(Accountno=5100718)
    return summary_foundry_metal[int(offset): int(offset) + int(limit)]


def is_there_more_data_foundry1(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_metal = summary_initial.filter(Accountno=5100717) | summary_initial.filter(Accountno=5100726) |\
                             summary_initial.filter(Accountno=5100716) | summary_initial.filter(Accountno=5100710) |\
                             summary_initial.filter(Accountno=5100715) | summary_initial.filter(Accountno=5100720) |\
                             summary_initial.filter(Accountno=5100719) | summary_initial.filter(Accountno=5100714) |\
                             summary_initial.filter(Accountno=5100711) | summary_initial.filter(Accountno=5100707) |\
                             summary_initial.filter(Accountno=5100712) | summary_initial.filter(Accountno=5100718)
    if int(offset) > summary_foundry_metal.count():
        return False
    return True


def BootstrapFilterView_foundry1(request):
    qs = filter_foundry1(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': FoundryMaterial.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_foundry1.html", context)

#end customize foundry chart metal

#start customize foundry chart labor

def is_valid_queryparam_foundry2(param):
    return param != '' and param is not None


def filter_foundry2(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_labor = summary_initial.filter(Accountno=5100100) | summary_initial.filter(Accountno=5100115) |\
                             summary_initial.filter(Accountno=5100103) | summary_initial.filter(Accountno=5100108) |\
                             summary_initial.filter(Accountno=5100125) | summary_initial.filter(Accountno=5100104) |\
                             summary_initial.filter(Accountno=5100111) | summary_initial.filter(Accountno=5100102) |\
                             summary_initial.filter(Accountno=5100110)
    qs = summary_foundry_labor.order_by('Transdate')
    categories = FoundryLabor.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_foundry2(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_foundry2(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_foundry2(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_foundry2(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_labor = summary_initial.filter(Accountno=5100100) | summary_initial.filter(Accountno=5100115) |\
                             summary_initial.filter(Accountno=5100103) | summary_initial.filter(Accountno=5100108) |\
                             summary_initial.filter(Accountno=5100125) | summary_initial.filter(Accountno=5100104) |\
                             summary_initial.filter(Accountno=5100111) | summary_initial.filter(Accountno=5100102) |\
                             summary_initial.filter(Accountno=5100110)
    return summary_foundry_labor[int(offset): int(offset) + int(limit)]


def is_there_more_data_foundry2(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_labor = summary_initial.filter(Accountno=5100100) | summary_initial.filter(Accountno=5100115) |\
                             summary_initial.filter(Accountno=5100103) | summary_initial.filter(Accountno=5100108) |\
                             summary_initial.filter(Accountno=5100125) | summary_initial.filter(Accountno=5100104) |\
                             summary_initial.filter(Accountno=5100111) | summary_initial.filter(Accountno=5100102) |\
                             summary_initial.filter(Accountno=5100110)
    if int(offset) > summary_foundry_labor.count():
        return False
    return True


def BootstrapFilterView_foundry2(request):
    qs = filter_foundry2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': FoundryLabor.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_foundry2.html", context)

#end customize foundry chart labor

#start customize foundry chart overhead

def is_valid_queryparam_foundry3(param):
    return param != '' and param is not None


def filter_foundry3(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_overhead = summary_initial.filter(Accountno=5100105) | summary_initial.filter(Accountno=5100120) |\
                             summary_initial.filter(Accountno=5100109) | summary_initial.filter(Accountno=5100126) |\
                             summary_initial.filter(Accountno=5100410) | summary_initial.filter(Accountno=5100820) |\
                             summary_initial.filter(Accountno=5100889) | summary_initial.filter(Accountno=5100902) |\
                             summary_initial.filter(Accountno=5100350) | summary_initial.filter(Accountno=5100310) |\
                             summary_initial.filter(Accountno=5100359) | summary_initial.filter(Accountno=5100363) |\
                             summary_initial.filter(Accountno=5100313) | summary_initial.filter(Accountno=5100352) |\
                             summary_initial.filter(Accountno=5100364) | summary_initial.filter(Accountno=5100360) |\
                             summary_initial.filter(Accountno=5100319) | summary_initial.filter(Accountno=5100355) |\
                             summary_initial.filter(Accountno=5100312) | summary_initial.filter(Accountno=5100320) |\
                             summary_initial.filter(Accountno=5100315) | summary_initial.filter(Accountno=5100311) |\
                             summary_initial.filter(Accountno=5100322) | summary_initial.filter(Accountno=5100316) |\
                             summary_initial.filter(Accountno=5100620) | summary_initial.filter(Accountno=5100210) |\
                             summary_initial.filter(Accountno=5100220) | summary_initial.filter(Accountno=5100230) |\
                             summary_initial.filter(Accountno=5100314) | summary_initial.filter(Accountno=5100317) |\
                             summary_initial.filter(Accountno=5100321) | summary_initial.filter(Accountno=5100351) |\
                             summary_initial.filter(Accountno=5100356) | summary_initial.filter(Accountno=5100357) |\
                             summary_initial.filter(Accountno=5100362) | summary_initial.filter(Accountno=5100510) |\
                             summary_initial.filter(Accountno=5100610) | summary_initial.filter(Accountno=5100615) |\
                             summary_initial.filter(Accountno=5100845) | summary_initial.filter(Accountno=5100862)
    qs = summary_foundry_overhead.order_by('Transdate')
    categories = FoundryOverhead.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_foundry3(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_foundry3(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_foundry3(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_foundry3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_overhead = summary_initial.filter(Accountno=5100105) | summary_initial.filter(Accountno=5100120) |\
                             summary_initial.filter(Accountno=5100109) | summary_initial.filter(Accountno=5100126) |\
                             summary_initial.filter(Accountno=5100410) | summary_initial.filter(Accountno=5100820) |\
                             summary_initial.filter(Accountno=5100889) | summary_initial.filter(Accountno=5100902) |\
                             summary_initial.filter(Accountno=5100350) | summary_initial.filter(Accountno=5100310) |\
                             summary_initial.filter(Accountno=5100359) | summary_initial.filter(Accountno=5100363) |\
                             summary_initial.filter(Accountno=5100313) | summary_initial.filter(Accountno=5100352) |\
                             summary_initial.filter(Accountno=5100364) | summary_initial.filter(Accountno=5100360) |\
                             summary_initial.filter(Accountno=5100319) | summary_initial.filter(Accountno=5100355) |\
                             summary_initial.filter(Accountno=5100312) | summary_initial.filter(Accountno=5100320) |\
                             summary_initial.filter(Accountno=5100315) | summary_initial.filter(Accountno=5100311) |\
                             summary_initial.filter(Accountno=5100322) | summary_initial.filter(Accountno=5100316) |\
                             summary_initial.filter(Accountno=5100620) | summary_initial.filter(Accountno=5100210) |\
                             summary_initial.filter(Accountno=5100220) | summary_initial.filter(Accountno=5100230) |\
                             summary_initial.filter(Accountno=5100314) | summary_initial.filter(Accountno=5100317) |\
                             summary_initial.filter(Accountno=5100321) | summary_initial.filter(Accountno=5100351) |\
                             summary_initial.filter(Accountno=5100356) | summary_initial.filter(Accountno=5100357) |\
                             summary_initial.filter(Accountno=5100362) | summary_initial.filter(Accountno=5100510) |\
                             summary_initial.filter(Accountno=5100610) | summary_initial.filter(Accountno=5100615) |\
                             summary_initial.filter(Accountno=5100845) | summary_initial.filter(Accountno=5100862)
    return summary_foundry_overhead[int(offset): int(offset) + int(limit)]


def is_there_more_data_foundry3(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_overhead = summary_initial.filter(Accountno=5100105) | summary_initial.filter(Accountno=5100120) |\
                             summary_initial.filter(Accountno=5100109) | summary_initial.filter(Accountno=5100126) |\
                             summary_initial.filter(Accountno=5100410) | summary_initial.filter(Accountno=5100820) |\
                             summary_initial.filter(Accountno=5100889) | summary_initial.filter(Accountno=5100902) |\
                             summary_initial.filter(Accountno=5100350) | summary_initial.filter(Accountno=5100310) |\
                             summary_initial.filter(Accountno=5100359) | summary_initial.filter(Accountno=5100363) |\
                             summary_initial.filter(Accountno=5100313) | summary_initial.filter(Accountno=5100352) |\
                             summary_initial.filter(Accountno=5100364) | summary_initial.filter(Accountno=5100360) |\
                             summary_initial.filter(Accountno=5100319) | summary_initial.filter(Accountno=5100355) |\
                             summary_initial.filter(Accountno=5100312) | summary_initial.filter(Accountno=5100320) |\
                             summary_initial.filter(Accountno=5100315) | summary_initial.filter(Accountno=5100311) |\
                             summary_initial.filter(Accountno=5100322) | summary_initial.filter(Accountno=5100316) |\
                             summary_initial.filter(Accountno=5100620) | summary_initial.filter(Accountno=5100210) |\
                             summary_initial.filter(Accountno=5100220) | summary_initial.filter(Accountno=5100230) |\
                             summary_initial.filter(Accountno=5100314) | summary_initial.filter(Accountno=5100317) |\
                             summary_initial.filter(Accountno=5100321) | summary_initial.filter(Accountno=5100351) |\
                             summary_initial.filter(Accountno=5100356) | summary_initial.filter(Accountno=5100357) |\
                             summary_initial.filter(Accountno=5100362) | summary_initial.filter(Accountno=5100510) |\
                             summary_initial.filter(Accountno=5100610) | summary_initial.filter(Accountno=5100615) |\
                             summary_initial.filter(Accountno=5100845) | summary_initial.filter(Accountno=5100862)
    if int(offset) > summary_foundry_overhead.count():
        return False
    return True


def BootstrapFilterView_foundry3(request):
    qs = filter_foundry3(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': FoundryOverhead.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_foundry3.html", context)

#end customize foundry chart overhead

@login_required
def foundry_chart(request):
    
    #start past three month foundry datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary_initial = GeneralReport.objects.filter(Transdate__range=[startdate, enddate]).filter(Transamnt__gt=0)
    recent_summary_foundry_metal = recent_summary_initial.filter(Accountno=5100717) | recent_summary_initial.filter(Accountno=5100726) |\
                             recent_summary_initial.filter(Accountno=5100716) | recent_summary_initial.filter(Accountno=5100710) |\
                             recent_summary_initial.filter(Accountno=5100715) | recent_summary_initial.filter(Accountno=5100720) |\
                             recent_summary_initial.filter(Accountno=5100719) | recent_summary_initial.filter(Accountno=5100714) |\
                             recent_summary_initial.filter(Accountno=5100711) | recent_summary_initial.filter(Accountno=5100707) |\
                             recent_summary_initial.filter(Accountno=5100712) |recent_summary_initial.filter(Accountno=5100718)
    recent_summary_metal = recent_summary_foundry_metal.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_metal =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_summary_metal},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'Accountno': 'Accountno',
                'metal cost': 'total'}]
                },

       
             ])

    recent_summary_foundry_labor = recent_summary_initial.filter(Accountno=5100100) | recent_summary_initial.filter(Accountno=5100115) |\
                             recent_summary_initial.filter(Accountno=5100103) | recent_summary_initial.filter(Accountno=5100108) |\
                             recent_summary_initial.filter(Accountno=5100125) | recent_summary_initial.filter(Accountno=5100104) |\
                             recent_summary_initial.filter(Accountno=5100111) | recent_summary_initial.filter(Accountno=5100102) |\
                             recent_summary_initial.filter(Accountno=5100110) 
    recent_summary_labor = recent_summary_foundry_labor.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_labor =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_summary_labor},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'Accountno': 'Accountno',
                'labor expense': 'total'}]
                },

       
             ])

    recent_summary_foundry_overhead = recent_summary_initial.filter(Accountno=5100105) | recent_summary_initial.filter(Accountno=5100120) |\
                             recent_summary_initial.filter(Accountno=5100109) | recent_summary_initial.filter(Accountno=5100126) |\
                             recent_summary_initial.filter(Accountno=5100410) | recent_summary_initial.filter(Accountno=5100820) |\
                             recent_summary_initial.filter(Accountno=5100889) | recent_summary_initial.filter(Accountno=5100902) |\
                             recent_summary_initial.filter(Accountno=5100350) | recent_summary_initial.filter(Accountno=5100310) |\
                             recent_summary_initial.filter(Accountno=5100359) | recent_summary_initial.filter(Accountno=5100363) |\
                             recent_summary_initial.filter(Accountno=5100313) | recent_summary_initial.filter(Accountno=5100352) |\
                             recent_summary_initial.filter(Accountno=5100364) | recent_summary_initial.filter(Accountno=5100360) |\
                             recent_summary_initial.filter(Accountno=5100319) | recent_summary_initial.filter(Accountno=5100355) |\
                             recent_summary_initial.filter(Accountno=5100312) | recent_summary_initial.filter(Accountno=5100320) |\
                             recent_summary_initial.filter(Accountno=5100315) | recent_summary_initial.filter(Accountno=5100311) |\
                             recent_summary_initial.filter(Accountno=5100322) | recent_summary_initial.filter(Accountno=5100316) |\
                             recent_summary_initial.filter(Accountno=5100620) | recent_summary_initial.filter(Accountno=5100210) |\
                             recent_summary_initial.filter(Accountno=5100220) | recent_summary_initial.filter(Accountno=5100230) |\
                             recent_summary_initial.filter(Accountno=5100314) | recent_summary_initial.filter(Accountno=5100317) |\
                             recent_summary_initial.filter(Accountno=5100321) | recent_summary_initial.filter(Accountno=5100351) |\
                             recent_summary_initial.filter(Accountno=5100356) | recent_summary_initial.filter(Accountno=5100357) |\
                             recent_summary_initial.filter(Accountno=5100362) | recent_summary_initial.filter(Accountno=5100510) |\
                             recent_summary_initial.filter(Accountno=5100610) | recent_summary_initial.filter(Accountno=5100615) |\
                             recent_summary_initial.filter(Accountno=5100845) | recent_summary_initial.filter(Accountno=5100862)
    recent_summary_overhead = recent_summary_foundry_overhead.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_overhead = DataPool(
           series=
            [{'options': {
            'source': recent_summary_overhead},
                'terms': [{'Accountno': 'Accountno',
                'overhead expense': 'total'}]
                },

       
             ])
    #end past three month datatable
    def glname(gl_num):
        names = {
            '5100100':'Direct Labor Salaries (FOUNDRY)', '5100115':'Health And Welfare (FOUNDRY)', '5100103':'Overtime/Double Time (FOUNDRY)', '5100108':'!W/C INS - Direct Labor (FOUNDRY)',
            '5100125':'Payroll Taxes Direct Labor (FOUNDRY)', '5100104':'Direct Labor Vacation (FOUNDRY)', '5100111':'Union 401K (FOUNDRY)', '5100102':'Direct Labor Incentives (FOUNDRY)',
            '5100110':'Union Pension (FOUNDRY)', '5100717':'Purchases Scrap (FOUNDRY)', '5100726':'Purchase - Extrusion Scrap (FOUNDRY)', '5100716':'Purchases Pig (FOUNDRY)',
            '5100710':'Purchases Log & Billet (FOUNDRY)', '5100715':'Purchases Magnesium (FOUNDRY)', '5100720':'Purchases Titaniun & Tibor (FOUNDRY)', '5100719':'Purchases Silicon (FOUNDRY)',
            '5100714':'Purchases Miscellaneous (FOUNDRY)', '5100711':'Purchases Copper (FOUNDRY)', '5100707':'Metal Hedging (Gain) / Loss (FOUNDRY)', '5100712':'Purchases Dross Conversion (FOUNDRY)',
            '5100718':'Purchases Rsi (FOUNDRY)', '5100105':'Indirect Salaries Supervision (FOUNDRY)', '5100120':'Hospitalization (FOUNDRY)', '5100109':'!W/C INS - IND DIR LABOR (FOUNDRY)',
            '5100126':'Payroll Taxes Indrect Labor (FOUNDRY)', '5100410':'Equipment Rental (FOUNDRY)','5100820':'Insurance Expense (FOUNDRY)', '5100889':'Placement Fee (FOUNDRY)',
            '5100902':'Depreciation Exp - M & E (FOUNDRY)','5100350':'Maintenance & Repair (FOUNDRY)','5100310':'Shop Supplies (FOUNDRY)','5100359':'Argon (FOUNDRY)','5100363':'Refractory Repairs (FOUNDRY)',
            '5100313':'Wagstaff Supplies & Equip (FOUNDRY)', '5100352':'Lift Truck Repairs (FOUNDRY)', '5100364':'Outside Mechanical (FOUNDRY)', '5100360':'Oven Repairs (FOUNDRY)',
            '5100319':'Thermocouple Tubes (FOUNDRY)', '5100355':'Gasoline (FOUNDRY)', '5100312':'Uniform Expense (FOUNDRY)', '5100320':'Hardware And Mill (FOUNDRY)',
            '5100315':'Filtration Supplies (FOUNDRY)', '5100311':'Saw Blades Expense (FOUNDRY)', '5100322':'Gloves (FOUNDRY)', '5100316':'Lubricants (FOUNDRY)', '5100620':'Entertainment (FOUNDRY)',
            '5100210':'Office Supplies (FOUNDRY)', '5100220':'Furniture & Fixtures Expense (FOUNDRY)', '5100230':'Computer Expense (FOUNDRY)', '5100314':'Degasser Flux (FOUNDRY)',
            '5100317':'Mach & Fabtn-O/S (FOUNDRY)', '5100321':'Electrical Expense (FOUNDRY)', '5100351':'Crane Repairs (FOUNDRY)', '5100356':'Pump Repairs (FOUNDRY)', '5100357':'Motor Repair (FOUNDRY)',
            '5100362':'Furnace Doors & Jambs (FOUNDRY)', '5100510':'Heat, Light & Power (FOUNDRY)', '5100610':'Travel Expense (FOUNDRY)', '5100615':'Buying Expense (FOUNDRY)',
            '5100845':'Truck And Aut (FOUNDRY)', '5100862':'5100862'
            }
        return names[gl_num]

    #start all time foundry datapool
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_metal = summary_initial.filter(Accountno=5100717) | summary_initial.filter(Accountno=5100726) |\
                             summary_initial.filter(Accountno=5100716) | summary_initial.filter(Accountno=5100710) |\
                             summary_initial.filter(Accountno=5100715) | summary_initial.filter(Accountno=5100720) |\
                             summary_initial.filter(Accountno=5100719) | summary_initial.filter(Accountno=5100714) |\
                             summary_initial.filter(Accountno=5100711) | summary_initial.filter(Accountno=5100707) |\
                             summary_initial.filter(Accountno=5100712) | summary_initial.filter(Accountno=5100718)
    summary_metal = summary_foundry_metal.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    metal =  DataPool(
           series=
            [{'options': {
            'source': summary_metal},
                'terms': [{'month': 'month',
                'metal cost': 'total'}]
                },

       
             ])

    summary_foundry_labor = summary_initial.filter(Accountno=5100100) | summary_initial.filter(Accountno=5100115) |\
                             summary_initial.filter(Accountno=5100103) | summary_initial.filter(Accountno=5100108) |\
                             summary_initial.filter(Accountno=5100125) | summary_initial.filter(Accountno=5100104) |\
                             summary_initial.filter(Accountno=5100111) | summary_initial.filter(Accountno=5100102) |\
                             summary_initial.filter(Accountno=5100110) 
    summary_labor = summary_foundry_labor.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    labor =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': summary_labor},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'month': 'month',
                'labor expense': 'total'}]
                },

       
             ])

    summary_foundry_overhead = summary_initial.filter(Accountno=5100105) | summary_initial.filter(Accountno=5100120) |\
                             summary_initial.filter(Accountno=5100109) | summary_initial.filter(Accountno=5100126) |\
                             summary_initial.filter(Accountno=5100410) | summary_initial.filter(Accountno=5100820) |\
                             summary_initial.filter(Accountno=5100889) | summary_initial.filter(Accountno=5100902) |\
                             summary_initial.filter(Accountno=5100350) | summary_initial.filter(Accountno=5100310) |\
                             summary_initial.filter(Accountno=5100359) | summary_initial.filter(Accountno=5100363) |\
                             summary_initial.filter(Accountno=5100313) | summary_initial.filter(Accountno=5100352) |\
                             summary_initial.filter(Accountno=5100364) | summary_initial.filter(Accountno=5100360) |\
                             summary_initial.filter(Accountno=5100319) | summary_initial.filter(Accountno=5100355) |\
                             summary_initial.filter(Accountno=5100312) | summary_initial.filter(Accountno=5100320) |\
                             summary_initial.filter(Accountno=5100315) | summary_initial.filter(Accountno=5100311) |\
                             summary_initial.filter(Accountno=5100322) | summary_initial.filter(Accountno=5100316) |\
                             summary_initial.filter(Accountno=5100620) | summary_initial.filter(Accountno=5100210) |\
                             summary_initial.filter(Accountno=5100220) | summary_initial.filter(Accountno=5100230) |\
                             summary_initial.filter(Accountno=5100314) | summary_initial.filter(Accountno=5100317) |\
                             summary_initial.filter(Accountno=5100321) | summary_initial.filter(Accountno=5100351) |\
                             summary_initial.filter(Accountno=5100356) | summary_initial.filter(Accountno=5100357) |\
                             summary_initial.filter(Accountno=5100362) | summary_initial.filter(Accountno=5100510) |\
                             summary_initial.filter(Accountno=5100610) | summary_initial.filter(Accountno=5100615) |\
                             summary_initial.filter(Accountno=5100845) | summary_initial.filter(Accountno=5100862)
    summary_overhead = summary_foundry_overhead.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    overhead = DataPool(
           series=
            [{'options': {
            'source': summary_overhead},
                'terms': [{'month': 'month',
                'overhead expense': 'total'}]
                },

       
             ])
    #end all time datapool

    #start past three months foundry chart
    cht10 = Chart(
            datasource = recent_metal,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'metal cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Metal Cost Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))  

    cht11 = Chart(
            datasource = recent_metal,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'metal cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Metal Cost Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht12 = Chart(
            datasource = recent_metal,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'metal cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Metal Cost Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht13 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Foundry Labor Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht14 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Foundry Labor Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht15 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Foundry Labor Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht16 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Foundry Overhead Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht17 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Foundry Overhead Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht18 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Foundry Overhead Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = metal,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'metal cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Metal Cost Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = metal,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'metal cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Metal Cost Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = metal,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'metal cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Metal Cost Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Labor Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Labor Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Labor Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht7 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Overhead Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht8 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Overhead Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht9 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Foundry Overhead Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    response = get_value(request.user.id)
    #end all time sales chart
    return render(request,'foundrychart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18],'response':response})


#start customize extrusion chart labor

def is_valid_queryparam_extrusion2(param):
    return param != '' and param is not None


def filter_extrusion2(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_labor = summary_initial.filter(Accountno=5400100) | summary_initial.filter(Accountno=5400115) |\
                             summary_initial.filter(Accountno=5400103) | summary_initial.filter(Accountno=5400108) |\
                             summary_initial.filter(Accountno=5400125) | summary_initial.filter(Accountno=5400104) |\
                             summary_initial.filter(Accountno=5400111) | summary_initial.filter(Accountno=5400102) |\
                             summary_initial.filter(Accountno=5400110)
    qs = summary_extrusion_labor.order_by('Transdate')
    categories = ExtrusionLabor.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_extrusion2(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_extrusion2(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_extrusion2(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_extrusion2(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_labor = summary_initial.filter(Accountno=5400100) | summary_initial.filter(Accountno=5400115) |\
                             summary_initial.filter(Accountno=5400103) | summary_initial.filter(Accountno=5400108) |\
                             summary_initial.filter(Accountno=5400125) | summary_initial.filter(Accountno=5400104) |\
                             summary_initial.filter(Accountno=5400111) | summary_initial.filter(Accountno=5400102) |\
                             summary_initial.filter(Accountno=5400110)
    return summary_extrusion_labor[int(offset): int(offset) + int(limit)]


def is_there_more_data_extrusion2(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_labor = summary_initial.filter(Accountno=5400100) | summary_initial.filter(Accountno=5400115) |\
                             summary_initial.filter(Accountno=5400103) | summary_initial.filter(Accountno=5400108) |\
                             summary_initial.filter(Accountno=5400125) | summary_initial.filter(Accountno=5400104) |\
                             summary_initial.filter(Accountno=5400111) | summary_initial.filter(Accountno=5400102) |\
                             summary_initial.filter(Accountno=5400110)
    if int(offset) > summary_extrusion_labor.count():
        return False
    return True


def BootstrapFilterView_extrusion2(request):
    qs = filter_extrusion2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': ExtrusionLabor.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_extrusion2.html", context)

#end customize extrusion chart labor

#start customize extrusion chart overhead

def is_valid_queryparam_extrusion3(param):
    return param != '' and param is not None


def filter_extrusion3(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_overhead = summary_initial.filter(Accountno=5400105) | summary_initial.filter(Accountno=5400350) |\
                             summary_initial.filter(Accountno=5400109) | summary_initial.filter(Accountno=5400126) |\
                             summary_initial.filter(Accountno=5400120) | summary_initial.filter(Accountno=5400334) |\
                             summary_initial.filter(Accountno=5400310) | summary_initial.filter(Accountno=5400311) |\
                             summary_initial.filter(Accountno=5400352) | summary_initial.filter(Accountno=5400333) |\
                             summary_initial.filter(Accountno=5400322) | summary_initial.filter(Accountno=5400332) |\
                             summary_initial.filter(Accountno=5400762) | summary_initial.filter(Accountno=5400364) |\
                             summary_initial.filter(Accountno=5400351) | summary_initial.filter(Accountno=5400357) |\
                             summary_initial.filter(Accountno=5400365) | summary_initial.filter(Accountno=5400331) |\
                             summary_initial.filter(Accountno=5400321) | summary_initial.filter(Accountno=5400354) |\
                             summary_initial.filter(Accountno=5400320) | summary_initial.filter(Accountno=5400410) |\
                             summary_initial.filter(Accountno=5400211) | summary_initial.filter(Accountno=5400220) |\
                             summary_initial.filter(Accountno=5400356) | summary_initial.filter(Accountno=5400358) |\
                             summary_initial.filter(Accountno=5400359) | summary_initial.filter(Accountno=5400362) |\
                             summary_initial.filter(Accountno=5400889) | summary_initial.filter(Accountno=5400000) |\
                             summary_initial.filter(Accountno=5400230) | summary_initial.filter(Accountno=5400353) |\
                             summary_initial.filter(Accountno=5400361) | summary_initial.filter(Accountno=5400806) |\
                             summary_initial.filter(Accountno=5400210) | summary_initial.filter(Accountno=5400335)
    qs = summary_extrusion_overhead.order_by('Transdate')
    categories = ExtrusionOverhead.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_extrusion3(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_extrusion3(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_extrusion3(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_extrusion3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_overhead = summary_initial.filter(Accountno=5400105) | summary_initial.filter(Accountno=5400350) |\
                             summary_initial.filter(Accountno=5400109) | summary_initial.filter(Accountno=5400126) |\
                             summary_initial.filter(Accountno=5400120) | summary_initial.filter(Accountno=5400334) |\
                             summary_initial.filter(Accountno=5400310) | summary_initial.filter(Accountno=5400311) |\
                             summary_initial.filter(Accountno=5400352) | summary_initial.filter(Accountno=5400333) |\
                             summary_initial.filter(Accountno=5400322) | summary_initial.filter(Accountno=5400332) |\
                             summary_initial.filter(Accountno=5400762) | summary_initial.filter(Accountno=5400364) |\
                             summary_initial.filter(Accountno=5400351) | summary_initial.filter(Accountno=5400357) |\
                             summary_initial.filter(Accountno=5400365) | summary_initial.filter(Accountno=5400331) |\
                             summary_initial.filter(Accountno=5400321) | summary_initial.filter(Accountno=5400354) |\
                             summary_initial.filter(Accountno=5400320) | summary_initial.filter(Accountno=5400410) |\
                             summary_initial.filter(Accountno=5400211) | summary_initial.filter(Accountno=5400220) |\
                             summary_initial.filter(Accountno=5400356) | summary_initial.filter(Accountno=5400358) |\
                             summary_initial.filter(Accountno=5400359) | summary_initial.filter(Accountno=5400362) |\
                             summary_initial.filter(Accountno=5400889) | summary_initial.filter(Accountno=5400000) |\
                             summary_initial.filter(Accountno=5400230) | summary_initial.filter(Accountno=5400353) |\
                             summary_initial.filter(Accountno=5400361) | summary_initial.filter(Accountno=5400806) |\
                             summary_initial.filter(Accountno=5400210) | summary_initial.filter(Accountno=5400335)
    return summary_extrusion_overhead[int(offset): int(offset) + int(limit)]


def is_there_more_data_extrusion3(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_overhead = summary_initial.filter(Accountno=5400105) | summary_initial.filter(Accountno=5400350) |\
                             summary_initial.filter(Accountno=5400109) | summary_initial.filter(Accountno=5400126) |\
                             summary_initial.filter(Accountno=5400120) | summary_initial.filter(Accountno=5400334) |\
                             summary_initial.filter(Accountno=5400310) | summary_initial.filter(Accountno=5400311) |\
                             summary_initial.filter(Accountno=5400352) | summary_initial.filter(Accountno=5400333) |\
                             summary_initial.filter(Accountno=5400322) | summary_initial.filter(Accountno=5400332) |\
                             summary_initial.filter(Accountno=5400762) | summary_initial.filter(Accountno=5400364) |\
                             summary_initial.filter(Accountno=5400351) | summary_initial.filter(Accountno=5400357) |\
                             summary_initial.filter(Accountno=5400365) | summary_initial.filter(Accountno=5400331) |\
                             summary_initial.filter(Accountno=5400321) | summary_initial.filter(Accountno=5400354) |\
                             summary_initial.filter(Accountno=5400320) | summary_initial.filter(Accountno=5400410) |\
                             summary_initial.filter(Accountno=5400211) | summary_initial.filter(Accountno=5400220) |\
                             summary_initial.filter(Accountno=5400356) | summary_initial.filter(Accountno=5400358) |\
                             summary_initial.filter(Accountno=5400359) | summary_initial.filter(Accountno=5400362) |\
                             summary_initial.filter(Accountno=5400889) | summary_initial.filter(Accountno=5400000) |\
                             summary_initial.filter(Accountno=5400230) | summary_initial.filter(Accountno=5400353) |\
                             summary_initial.filter(Accountno=5400361) | summary_initial.filter(Accountno=5400806) |\
                             summary_initial.filter(Accountno=5400210) | summary_initial.filter(Accountno=5400335)
    if int(offset) > summary_extrusion_overhead.count():
        return False
    return True


def BootstrapFilterView_extrusion3(request):
    qs = filter_extrusion3(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': ExtrusionOverhead.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_extrusion3.html", context)

#end customize extrusion chart overhead

@login_required
def extrusion_chart(request):
    #start past three month extrusion datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary_initial = GeneralReport.objects.filter(Transdate__range=[startdate, enddate]).filter(Transamnt__gt=0)

    recent_summary_extrusion_total = recent_summary_initial.filter(Accountno__gte = 5400000) & recent_summary_initial.filter(Accountno__lt = 5410000)
    recent_summary_total = recent_summary_extrusion_total.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_total =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_summary_total},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'Accountno': 'Accountno',
                'total expense': 'total'}]
                },

       
             ])
    
    recent_summary_extrusion_labor = recent_summary_initial.filter(Accountno=5400100) | recent_summary_initial.filter(Accountno=5400115) |\
                             recent_summary_initial.filter(Accountno=5400103) | recent_summary_initial.filter(Accountno=5400108) |\
                             recent_summary_initial.filter(Accountno=5400125) | recent_summary_initial.filter(Accountno=5400104) |\
                             recent_summary_initial.filter(Accountno=5400111) | recent_summary_initial.filter(Accountno=5400102) |\
                             recent_summary_initial.filter(Accountno=5400110) 
    recent_summary_labor = recent_summary_extrusion_labor.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_labor =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_summary_labor},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'Accountno': 'Accountno',
                'labor expense': 'total'}]
                },

       
             ])

    recent_summary_extrusion_overhead = recent_summary_initial.filter(Accountno=5400105) | recent_summary_initial.filter(Accountno=5400350) |\
                             recent_summary_initial.filter(Accountno=5400109) | recent_summary_initial.filter(Accountno=5400126) |\
                             recent_summary_initial.filter(Accountno=5400120) | recent_summary_initial.filter(Accountno=5400334) |\
                             recent_summary_initial.filter(Accountno=5400310) | recent_summary_initial.filter(Accountno=5400311) |\
                             recent_summary_initial.filter(Accountno=5400352) | recent_summary_initial.filter(Accountno=5400333) |\
                             recent_summary_initial.filter(Accountno=5400322) | recent_summary_initial.filter(Accountno=5400332) |\
                             recent_summary_initial.filter(Accountno=5400762) | recent_summary_initial.filter(Accountno=5400364) |\
                             recent_summary_initial.filter(Accountno=5400351) | recent_summary_initial.filter(Accountno=5400357) |\
                             recent_summary_initial.filter(Accountno=5400365) | recent_summary_initial.filter(Accountno=5400331) |\
                             recent_summary_initial.filter(Accountno=5400321) | recent_summary_initial.filter(Accountno=5400354) |\
                             recent_summary_initial.filter(Accountno=5400320) | recent_summary_initial.filter(Accountno=5400410) |\
                             recent_summary_initial.filter(Accountno=5400211) | recent_summary_initial.filter(Accountno=5400220) |\
                             recent_summary_initial.filter(Accountno=5400356) | recent_summary_initial.filter(Accountno=5400358) |\
                             recent_summary_initial.filter(Accountno=5400359) | recent_summary_initial.filter(Accountno=5400362) |\
                             recent_summary_initial.filter(Accountno=5400889) | recent_summary_initial.filter(Accountno=5400000) |\
                             recent_summary_initial.filter(Accountno=5400230) | recent_summary_initial.filter(Accountno=5400353) |\
                             recent_summary_initial.filter(Accountno=5400361) | recent_summary_initial.filter(Accountno=5400806) |\
                             recent_summary_initial.filter(Accountno=5400210) | recent_summary_initial.filter(Accountno=5400335)
    recent_summary_overhead = recent_summary_extrusion_overhead.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_overhead = DataPool(
           series=
            [{'options': {
            'source': recent_summary_overhead},
                'terms': [{'Accountno': 'Accountno',
                'overhead expense': 'total'}]
                },

       
             ])
    #end past three month datatable
    def glname(gl_num):
        names = {
            '5400100':'Direct Labor Salaries (EXTRUSION)', '5400115':'Health And Welfare (EXTRUSION)', '5400103':'Overtime/Double Time (EXTRUSION)', '5400108':'!W/C INS - Direct Labor (EXTRUSION)',
            '5400125':'Payroll Taxes Direct Labor (EXTRUSION)', '5400104':'Direct Labor Vacation (EXTRUSION)', '5400111':'Union 401K (EXTRUSION)', '5400102':'Direct Labor Incentives (EXTRUSION)',
            '5400110':'Union Pension (EXTRUSION)', '5400105':'Indirect Salaries Supervision (EXTRUSION)', '5400350':'Maintenance & Repairs (EXTRUSION)', '5400109':'!W/C INS - IND DIR LABOR (EXTRUSION)',
            '5400126':'Payroll Taxes Indirect Labor (EXTRUSION)', '5400120':'Hospitalization (EXTRUSION)', '5400334':'Oil & Fluids (EXTRUSION)', '5400310':'Shop Supplies (EXTRUSION)',
            '5400311':'Saw Blades (EXTRUSION)', '5400352':'Lift Truck Expense (EXTRUSION)', '5400333':'Lubricants (EXTRUSION)', '5400322':'Gloves & Personal Equip (EXTRUSION)',
            '5400332':'Nitrogen (EXTRUSION)', '5400762':'STRAPPING,PACKAGING (EXTRUSION)', '5400364':'Outside Mechanical (EXTRUSION)', '5400351':'Crane Expense (EXTRUSION)',
            '5400357':'Motor Repair (EXTRUSION)', '5400365':'Outside Electrical (EXTRUSION)', '5400331':'Filters (EXTRUSION)', '5400321':'Electrical Expense (EXTRUSION)',
            '5400354':'Quality Control (EXTRUSION)', '5400320':'Hardware And Mill (EXTRUSION)', '5400410':'Equipment Rental (EXTRUSION)', '5400211':'Commissions (Extrusions)',
            '5400220':'Furniture & Fixtures Expense (EXTRUSION)', '5400356':'Pump Repair (EXTRUSION)','5400358':'Billet Heater Repairs (EXTRUSION)', '5400359':'Handling Equipment Repairs (EXTRUSION)',
            '5400362':'Fixed Heads (EXTRUSION)', '5400889':'Placement Fee (EXTRUSION)', '5400000':'5400000', '5400230':'Computer Expense (EXTRUSION)', '5400353':'Racking Expense (EXTRUSION)',
            '5400361':'Aliminum Cutting (EXTRUSION)', '5400806':'CONSULTING/TEMPORARY PERSONNEL (EXTRUSION)', '5400210':'Office Supplies (EXTRUSION)', '5400335':'Steel Expense (EXTRUSION)'
            }
        return names[gl_num]
    #start all time foundry datapool
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_extrusion_total = summary_initial.filter(Accountno__gte = 5400000) & summary_initial.filter(Accountno__lt = 5410000)
    summary_total = summary_extrusion_total.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    total =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': summary_total},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'month': 'month',
                'total expense': 'total'}]
                },

       
             ])

    summary_extrusion_labor = summary_initial.filter(Accountno=5400100) | summary_initial.filter(Accountno=5400115) |\
                             summary_initial.filter(Accountno=5400103) | summary_initial.filter(Accountno=5400108) |\
                             summary_initial.filter(Accountno=5400125) | summary_initial.filter(Accountno=5400104) |\
                             summary_initial.filter(Accountno=5400111) | summary_initial.filter(Accountno=5400102) |\
                             summary_initial.filter(Accountno=5400110) 
    summary_labor = summary_extrusion_labor.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    labor =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': summary_labor},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'month': 'month',
                'labor expense': 'total'}]
                },

       
             ])

    summary_extrusion_overhead = summary_initial.filter(Accountno=5400105) | summary_initial.filter(Accountno=5400350) |\
                             summary_initial.filter(Accountno=5400109) | summary_initial.filter(Accountno=5400126) |\
                             summary_initial.filter(Accountno=5400120) | summary_initial.filter(Accountno=5400334) |\
                             summary_initial.filter(Accountno=5400310) | summary_initial.filter(Accountno=5400311) |\
                             summary_initial.filter(Accountno=5400352) | summary_initial.filter(Accountno=5400333) |\
                             summary_initial.filter(Accountno=5400322) | summary_initial.filter(Accountno=5400332) |\
                             summary_initial.filter(Accountno=5400762) | summary_initial.filter(Accountno=5400364) |\
                             summary_initial.filter(Accountno=5400351) | summary_initial.filter(Accountno=5400357) |\
                             summary_initial.filter(Accountno=5400365) | summary_initial.filter(Accountno=5400331) |\
                             summary_initial.filter(Accountno=5400321) | summary_initial.filter(Accountno=5400354) |\
                             summary_initial.filter(Accountno=5400320) | summary_initial.filter(Accountno=5400410) |\
                             summary_initial.filter(Accountno=5400211) | summary_initial.filter(Accountno=5400220) |\
                             summary_initial.filter(Accountno=5400356) | summary_initial.filter(Accountno=5400358) |\
                             summary_initial.filter(Accountno=5400359) | summary_initial.filter(Accountno=5400362) |\
                             summary_initial.filter(Accountno=5400889) | summary_initial.filter(Accountno=5400000) |\
                             summary_initial.filter(Accountno=5400230) | summary_initial.filter(Accountno=5400353) |\
                             summary_initial.filter(Accountno=5400361) | summary_initial.filter(Accountno=5400806) |\
                             summary_initial.filter(Accountno=5400210) | summary_initial.filter(Accountno=5400335)
    summary_overhead = summary_extrusion_overhead.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    overhead = DataPool(
           series=
            [{'options': {
            'source': summary_overhead},
                'terms': [{'month': 'month',
                'overhead expense': 'total'}]
                },

       
             ])
    #end all time datapool

    #start past three months foundry chart
    cht10 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Total Cost Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))  

    cht11 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Total Cost Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht12 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Total Cost Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht13 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Extrusion Labor Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht14 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Extrusion Labor Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht15 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Extrusion Labor Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht16 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Extrusion Overhead Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht17 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Extrusion Overhead Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht18 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Extrusion Overhead Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Total Cost Amount All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Total Cost Amount All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Total Cost Amount All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Labor Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Labor Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Labor Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht7 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Overhead Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht8 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Overhead Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht9 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Extrusion Overhead Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    response = get_value(request.user.id)

    #end all time sales chart
    return render(request,'extrusionchart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18],'response':response})

#start customize fabrication chart labor

def is_valid_queryparam_fabrication2(param):
    return param != '' and param is not None


def filter_fabrication2(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_labor = summary_initial.filter(Accountno=5650100) | summary_initial.filter(Accountno=5650115) |\
                             summary_initial.filter(Accountno=5650103) | summary_initial.filter(Accountno=5650108) |\
                             summary_initial.filter(Accountno=5650125) | summary_initial.filter(Accountno=5650104) |\
                             summary_initial.filter(Accountno=5650111) | summary_initial.filter(Accountno=5650102) |\
                             summary_initial.filter(Accountno=5650110)
    qs = summary_fabrication_labor.order_by('Transdate')
    categories = FabricationLabor.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_fabrication2(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_fabrication2(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_fabrication2(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_fabrication2(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_labor = summary_initial.filter(Accountno=5650100) | summary_initial.filter(Accountno=5650115) |\
                             summary_initial.filter(Accountno=5650103) | summary_initial.filter(Accountno=5650108) |\
                             summary_initial.filter(Accountno=5650125) | summary_initial.filter(Accountno=5650104) |\
                             summary_initial.filter(Accountno=5650111) | summary_initial.filter(Accountno=5650102) |\
                             summary_initial.filter(Accountno=5650110)
    return summary_fabrication_labor[int(offset): int(offset) + int(limit)]


def is_there_more_data_fabrication2(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_labor = summary_initial.filter(Accountno=5650100) | summary_initial.filter(Accountno=5650115) |\
                             summary_initial.filter(Accountno=5650103) | summary_initial.filter(Accountno=5650108) |\
                             summary_initial.filter(Accountno=5650125) | summary_initial.filter(Accountno=5650104) |\
                             summary_initial.filter(Accountno=5650111) | summary_initial.filter(Accountno=5650102) |\
                             summary_initial.filter(Accountno=5650110)
    if int(offset) > summary_fabrication_labor.count():
        return False
    return True


def BootstrapFilterView_fabrication2(request):
    qs = filter_fabrication2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': FabricationLabor.objects.all(),
        'response':response
    }

    return render(request, "bootstrap_form_fabrication2.html", context)

#end customize fabrication chart labor

#start customize fabrication chart overhead

def is_valid_queryparam_fabrication3(param):
    return param != '' and param is not None


def filter_fabrication3(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_overhead = summary_initial.filter(Accountno=5650105) | summary_initial.filter(Accountno=5650120) |\
                             summary_initial.filter(Accountno=5650109) | summary_initial.filter(Accountno=5650126) |\
                             summary_initial.filter(Accountno=5650350) | summary_initial.filter(Accountno=5650310) |\
                             summary_initial.filter(Accountno=5650309) | summary_initial.filter(Accountno=5650311) |\
                             summary_initial.filter(Accountno=5650352) | summary_initial.filter(Accountno=5650410) |\
                             summary_initial.filter(Accountno=5650106) | summary_initial.filter(Accountno=5650220) |\
                             summary_initial.filter(Accountno=5650308) | summary_initial.filter(Accountno=5650357) |\
                             summary_initial.filter(Accountno=5650368) | summary_initial.filter(Accountno=5650112) |\
                             summary_initial.filter(Accountno=5650321) | summary_initial.filter(Accountno=5650210) |\
                             summary_initial.filter(Accountno=5650320) | summary_initial.filter(Accountno=5650323) |\
                             summary_initial.filter(Accountno=5650211)
    qs = summary_fabrication_overhead.order_by('Transdate')
    categories = FabricationOverhead.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_fabrication3(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_fabrication3(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_fabrication3(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_fabrication3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_overhead = summary_initial.filter(Accountno=5650105) | summary_initial.filter(Accountno=5650120) |\
                             summary_initial.filter(Accountno=5650109) | summary_initial.filter(Accountno=5650126) |\
                             summary_initial.filter(Accountno=5650350) | summary_initial.filter(Accountno=5650310) |\
                             summary_initial.filter(Accountno=5650309) | summary_initial.filter(Accountno=5650311) |\
                             summary_initial.filter(Accountno=5650352) | summary_initial.filter(Accountno=5650410) |\
                             summary_initial.filter(Accountno=5650106) | summary_initial.filter(Accountno=5650220) |\
                             summary_initial.filter(Accountno=5650308) | summary_initial.filter(Accountno=5650357) |\
                             summary_initial.filter(Accountno=5650368) | summary_initial.filter(Accountno=5650112) |\
                             summary_initial.filter(Accountno=5650321) | summary_initial.filter(Accountno=5650210) |\
                             summary_initial.filter(Accountno=5650320) | summary_initial.filter(Accountno=5650323) |\
                             summary_initial.filter(Accountno=5650211)
    return summary_fabrication_overhead[int(offset): int(offset) + int(limit)]


def is_there_more_data_fabrication3(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_overhead = summary_initial.filter(Accountno=5650105) | summary_initial.filter(Accountno=5650120) |\
                             summary_initial.filter(Accountno=5650109) | summary_initial.filter(Accountno=5650126) |\
                             summary_initial.filter(Accountno=5650350) | summary_initial.filter(Accountno=5650310) |\
                             summary_initial.filter(Accountno=5650309) | summary_initial.filter(Accountno=5650311) |\
                             summary_initial.filter(Accountno=5650352) | summary_initial.filter(Accountno=5650410) |\
                             summary_initial.filter(Accountno=5650106) | summary_initial.filter(Accountno=5650220) |\
                             summary_initial.filter(Accountno=5650308) | summary_initial.filter(Accountno=5650357) |\
                             summary_initial.filter(Accountno=5650368) | summary_initial.filter(Accountno=5650112) |\
                             summary_initial.filter(Accountno=5650321) | summary_initial.filter(Accountno=5650210) |\
                             summary_initial.filter(Accountno=5650320) | summary_initial.filter(Accountno=5650323) |\
                             summary_initial.filter(Accountno=5650211)
    if int(offset) > summary_fabrication_overhead.count():
        return False
    return True


def BootstrapFilterView_fabrication3(request):
    qs = filter_fabrication3(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': FabricationOverhead.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_fabrication3.html", context)

#end customize fabrication chart overhead

@login_required
def fabrication_chart(request):
    #start past three month foundry datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary_initial = GeneralReport.objects.filter(Transdate__range=[startdate, enddate]).filter(Transamnt__gt=0)
    recent_summary_fabrication_material = recent_summary_initial.filter(Accountno=5650702)
    recent_summary_material = recent_summary_fabrication_material.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_material =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_material},
                'terms': [{'Accountno': 'Accountno',
                'material cost': 'total'}]
                },

       
             ])

    recent_summary_fabrication_labor = recent_summary_initial.filter(Accountno=5650100) | recent_summary_initial.filter(Accountno=5650115) |\
                             recent_summary_initial.filter(Accountno=5650103) | recent_summary_initial.filter(Accountno=5650108) |\
                             recent_summary_initial.filter(Accountno=5650125) | recent_summary_initial.filter(Accountno=5650104) |\
                             recent_summary_initial.filter(Accountno=5650111) | recent_summary_initial.filter(Accountno=5650102) |\
                             recent_summary_initial.filter(Accountno=5650110) 
    recent_summary_labor = recent_summary_fabrication_labor.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_labor =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_labor},
                'terms': [{'Accountno': 'Accountno',
                'labor expense': 'total'}]
                },

       
             ])

    recent_summary_fabrication_overhead = recent_summary_initial.filter(Accountno=5650105) | recent_summary_initial.filter(Accountno=5650120) |\
                             recent_summary_initial.filter(Accountno=5650109) | recent_summary_initial.filter(Accountno=5650126) |\
                             recent_summary_initial.filter(Accountno=5650350) | recent_summary_initial.filter(Accountno=5650310) |\
                             recent_summary_initial.filter(Accountno=5650309) | recent_summary_initial.filter(Accountno=5650311) |\
                             recent_summary_initial.filter(Accountno=5650352) | recent_summary_initial.filter(Accountno=5650410) |\
                             recent_summary_initial.filter(Accountno=5650106) | recent_summary_initial.filter(Accountno=5650220) |\
                             recent_summary_initial.filter(Accountno=5650308) | recent_summary_initial.filter(Accountno=5650357) |\
                             recent_summary_initial.filter(Accountno=5650368) | recent_summary_initial.filter(Accountno=5650112) |\
                             recent_summary_initial.filter(Accountno=5650321) | recent_summary_initial.filter(Accountno=5650210) |\
                             recent_summary_initial.filter(Accountno=5650320) | recent_summary_initial.filter(Accountno=5650323) |\
                             recent_summary_initial.filter(Accountno=5650211)
    recent_summary_overhead = recent_summary_fabrication_overhead.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_overhead = DataPool(
           series=
            [{'options': {
            'source': recent_summary_overhead},
                'terms': [{'Accountno': 'Accountno',
                'overhead expense': 'total'}]
                },

       
             ])
    #end past three month datatable

    def glname(gl_num):
        names = {
            '5650100':'Direct Labor Salaries (FABRICATION)', '5650115':'Health And Welfare (FABRICATION)', '5650103':'Overtime/Double Time (FABRICATION)', '5650108':'!W/C INS - Direct Labor (FABRICATION)',
            '5650125':'Payroll Taxes Direct Labor (FABRICATION)', '5650104':'Direct Labor Vacation (FABRICATION)', '5650111':'Union 401K (FABRICATION)', '5650102':'Direct Labor Incentives (FABRICATION)',
            '5650110':'Union Pension (FABRICATION)', '5650105':'Indirect Salaries Supervision (FABRICATION)', '5650120':'Hospitalization (FABRICATION)', '5650109':'!W/C INS - IND DIR LABOR (FABRICATION)',
            '5650126':'Payroll Taxes Indirect Labor (FABRICATION)', '5650350':'Maintenance & Repairs (FABRICATION)', '5650310':'Shop Supplies (FABRICATION)', '5650309':'Tooling Expense (FABRICATION)',
            '5650311':'Saw Blades (FABRICATION)', '5650352':'Lift Truck Repairs (FABRICATION)', '5650410':'Equipment Rental (FABRICATION)', '5650106':'Welding - Delair Services (FABRICATION)',
            '5650220':'Furniture & Fixtures Expense (FABRICATION)', '5650308':'Tooling Maintenance (FABRICATION)', '5650357':'Motor Repair (FABRICATION)',
            '5650368':'Equipment Repair (FABRICATION)', '5650112':'Labor Transfer In/(Out) (FABRICATION)', '5650321':'Electrical Expense (FABRICATION)',
            '5650210':'Office Supplies (FABRICATION)', '5650320':'Hardware And Mill (FABRICATION)', '5650323':'Fence Assembly Misc Parts (FABRICATION)', '5650211':'Salesman Commissions (FABRICATION)',
            '5650702':'Purchase Fabrication'
            }
        return names[gl_num]

    #start all time foundry datapool
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_fabrication_material = summary_initial.filter(Accountno=5650702)
    summary_material = summary_fabrication_material.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    material =  DataPool(
           series=
            [{'options': {
            'source': summary_material},
                'terms': [{'month': 'month',
                'material cost': 'total'}]
                },

       
             ])

    summary_fabrication_labor = summary_initial.filter(Accountno=5650100) | summary_initial.filter(Accountno=5650115) |\
                             summary_initial.filter(Accountno=5650103) | summary_initial.filter(Accountno=5650108) |\
                             summary_initial.filter(Accountno=5650125) | summary_initial.filter(Accountno=5650104) |\
                             summary_initial.filter(Accountno=5650111) | summary_initial.filter(Accountno=5650102) |\
                             summary_initial.filter(Accountno=5650110) 
    summary_labor = summary_fabrication_labor.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    labor =  DataPool(
           series=
            [{'options': {
            'source': summary_labor},
                'terms': [{'month': 'month',
                'labor expense': 'total'}]
                },

       
             ])

    summary_fabrication_overhead = summary_initial.filter(Accountno=5650105) | summary_initial.filter(Accountno=5650120) |\
                             summary_initial.filter(Accountno=5650109) | summary_initial.filter(Accountno=5650126) |\
                             summary_initial.filter(Accountno=5650350) | summary_initial.filter(Accountno=5650310) |\
                             summary_initial.filter(Accountno=5650309) | summary_initial.filter(Accountno=5650311) |\
                             summary_initial.filter(Accountno=5650352) | summary_initial.filter(Accountno=5650410) |\
                             summary_initial.filter(Accountno=5650106) | summary_initial.filter(Accountno=5650220) |\
                             summary_initial.filter(Accountno=5650308) | summary_initial.filter(Accountno=5650357) |\
                             summary_initial.filter(Accountno=5650368) | summary_initial.filter(Accountno=5650112) |\
                             summary_initial.filter(Accountno=5650321) | summary_initial.filter(Accountno=5650210) |\
                             summary_initial.filter(Accountno=5650320) | summary_initial.filter(Accountno=5650323) |\
                             summary_initial.filter(Accountno=5650211)
    summary_overhead = summary_fabrication_overhead.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    overhead = DataPool(
           series=
            [{'options': {
            'source': summary_overhead},
                'terms': [{'month': 'month',
                'overhead expense': 'total'}]
                },

       
             ])
    #end all time datapool

    #start past three months foundry chart
    cht10 = Chart(
            datasource = recent_material,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Material Cost Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))  

    cht11 = Chart(
            datasource = recent_material,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Material Cost Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht12 = Chart(
            datasource = recent_material,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Material Cost Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht13 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Fabrication Labor Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht14 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Fabrication Labor Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht15 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Fabrication Labor Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht16 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Fabrication Overhead Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht17 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Fabrication Overhead Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht18 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Fabrication Overhead Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = material,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Material Cost Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = material,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Material Cost Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = material,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Material Cost Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Labor Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Labor Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Labor Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht7 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Overhead Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht8 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Overhead Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht9 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Fabrication Overhead Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end all time sales chart
    response = get_value(request.user.id)
    return render(request,'fabricationchart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18],'response':response})


#start customize anodizing chart labor

def is_valid_queryparam_anodizing2(param):
    return param != '' and param is not None


def filter_anodizing2(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_labor = summary_initial.filter(Accountno=5750100) | summary_initial.filter(Accountno=5750115) |\
                             summary_initial.filter(Accountno=5750103) | summary_initial.filter(Accountno=5750108) |\
                             summary_initial.filter(Accountno=5750125) | summary_initial.filter(Accountno=5750104) |\
                             summary_initial.filter(Accountno=5750111) | summary_initial.filter(Accountno=5750102) |\
                             summary_initial.filter(Accountno=5750110)
    qs = summary_anodizing_labor.order_by('Transdate')
    categories = AnodizingLabor.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_anodizing2(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_anodizing2(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_anodizing2(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_anodizing2(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_labor = summary_initial.filter(Accountno=5750100) | summary_initial.filter(Accountno=5750115) |\
                             summary_initial.filter(Accountno=5750103) | summary_initial.filter(Accountno=5750108) |\
                             summary_initial.filter(Accountno=5750125) | summary_initial.filter(Accountno=5750104) |\
                             summary_initial.filter(Accountno=5750111) | summary_initial.filter(Accountno=5750102) |\
                             summary_initial.filter(Accountno=5750110)
    return summary_anodizing_labor[int(offset): int(offset) + int(limit)]


def is_there_more_data_anodizing2(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_labor = summary_initial.filter(Accountno=5750100) | summary_initial.filter(Accountno=5750115) |\
                             summary_initial.filter(Accountno=5750103) | summary_initial.filter(Accountno=5750108) |\
                             summary_initial.filter(Accountno=5750125) | summary_initial.filter(Accountno=5750104) |\
                             summary_initial.filter(Accountno=5750111) | summary_initial.filter(Accountno=5750102) |\
                             summary_initial.filter(Accountno=5750110)
    if int(offset) > summary_anodizing_labor.count():
        return False
    return True


def BootstrapFilterView_anodizing2(request):
    qs = filter_anodizing2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': AnodizingLabor.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_anodizing2.html", context)

#end customize anodizing chart labor


#start customize anodizing chart overhead

def is_valid_queryparam_anodizing3(param):
    return param != '' and param is not None


def filter_anodizing3(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_overhead = summary_initial.filter(Accountno=5750105) | summary_initial.filter(Accountno=5750350) |\
                             summary_initial.filter(Accountno=5750410) | summary_initial.filter(Accountno=5750120) |\
                             summary_initial.filter(Accountno=5750310) | summary_initial.filter(Accountno=5750109) |\
                             summary_initial.filter(Accountno=5750126) | summary_initial.filter(Accountno=5750352) |\
                             summary_initial.filter(Accountno=5750211) | summary_initial.filter(Accountno=5750900) |\
                             summary_initial.filter(Accountno=5750351) | summary_initial.filter(Accountno=5750356) |\
                             summary_initial.filter(Accountno=5750357) | summary_initial.filter(Accountno=5750364) |\
                             summary_initial.filter(Accountno=5750112) | summary_initial.filter(Accountno=5750230) |\
                             summary_initial.filter(Accountno=5750321) | summary_initial.filter(Accountno=5750610) |\
                             summary_initial.filter(Accountno=5750705) | summary_initial.filter(Accountno=5750800) |\
                             summary_initial.filter(Accountno=5750806) | summary_initial.filter(Accountno=5750210) |\
                             summary_initial.filter(Accountno=5750210) | summary_initial.filter(Accountno=5750702) |\
                             summary_initial.filter(Accountno=5750510)
    qs = summary_anodizing_overhead.order_by('Transdate')
    categories = AnodizingOverhead.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_anodizing3(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_anodizing3(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_anodizing3(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_anodizing3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_overhead = summary_initial.filter(Accountno=5750105) | summary_initial.filter(Accountno=5750350) |\
                             summary_initial.filter(Accountno=5750410) | summary_initial.filter(Accountno=5750120) |\
                             summary_initial.filter(Accountno=5750310) | summary_initial.filter(Accountno=5750109) |\
                             summary_initial.filter(Accountno=5750126) | summary_initial.filter(Accountno=5750352) |\
                             summary_initial.filter(Accountno=5750211) | summary_initial.filter(Accountno=5750900) |\
                             summary_initial.filter(Accountno=5750351) | summary_initial.filter(Accountno=5750356) |\
                             summary_initial.filter(Accountno=5750357) | summary_initial.filter(Accountno=5750364) |\
                             summary_initial.filter(Accountno=5750112) | summary_initial.filter(Accountno=5750230) |\
                             summary_initial.filter(Accountno=5750321) | summary_initial.filter(Accountno=5750610) |\
                             summary_initial.filter(Accountno=5750705) | summary_initial.filter(Accountno=5750800) |\
                             summary_initial.filter(Accountno=5750806) | summary_initial.filter(Accountno=5750210) |\
                             summary_initial.filter(Accountno=5750210) | summary_initial.filter(Accountno=5750702) |\
                             summary_initial.filter(Accountno=5750510)
    return summary_anodizing_overhead[int(offset): int(offset) + int(limit)]


def is_there_more_data_anodizing3(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_overhead = summary_initial.filter(Accountno=5750105) | summary_initial.filter(Accountno=5750350) |\
                             summary_initial.filter(Accountno=5750410) | summary_initial.filter(Accountno=5750120) |\
                             summary_initial.filter(Accountno=5750310) | summary_initial.filter(Accountno=5750109) |\
                             summary_initial.filter(Accountno=5750126) | summary_initial.filter(Accountno=5750352) |\
                             summary_initial.filter(Accountno=5750211) | summary_initial.filter(Accountno=5750900) |\
                             summary_initial.filter(Accountno=5750351) | summary_initial.filter(Accountno=5750356) |\
                             summary_initial.filter(Accountno=5750357) | summary_initial.filter(Accountno=5750364) |\
                             summary_initial.filter(Accountno=5750112) | summary_initial.filter(Accountno=5750230) |\
                             summary_initial.filter(Accountno=5750321) | summary_initial.filter(Accountno=5750610) |\
                             summary_initial.filter(Accountno=5750705) | summary_initial.filter(Accountno=5750800) |\
                             summary_initial.filter(Accountno=5750806) | summary_initial.filter(Accountno=5750210) |\
                             summary_initial.filter(Accountno=5750210) | summary_initial.filter(Accountno=5750702) |\
                             summary_initial.filter(Accountno=5750510)
    if int(offset) > summary_anodizing_overhead.count():
        return False
    return True


def BootstrapFilterView_anodizing3(request):
    qs = filter_anodizing3(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': AnodizingOverhead.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_anodizing3.html", context)

#end customize anodizing chart overhead

@login_required
def anodizing_chart(request):
    #start past three month foundry datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary_initial = GeneralReport.objects.filter(Transdate__range=[startdate, enddate]).filter(Transamnt__gt=0)
    recent_summary_anodizing_material = recent_summary_initial.filter(Accountno=5750701)
    recent_summary_material = recent_summary_anodizing_material.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_material =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_material},
                'terms': [{'Accountno': 'Accountno',
                'material cost': 'total'}]
                },

       
             ])

    recent_summary_anodizing_labor = recent_summary_initial.filter(Accountno=5750100) | recent_summary_initial.filter(Accountno=5750115) |\
                             recent_summary_initial.filter(Accountno=5750103) | recent_summary_initial.filter(Accountno=5750108) |\
                             recent_summary_initial.filter(Accountno=5750125) | recent_summary_initial.filter(Accountno=5750104) |\
                             recent_summary_initial.filter(Accountno=5750111) | recent_summary_initial.filter(Accountno=5750102) |\
                             recent_summary_initial.filter(Accountno=5750110) 
    recent_summary_labor = recent_summary_anodizing_labor.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_labor =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_labor},
                'terms': [{'Accountno': 'Accountno',
                'labor expense': 'total'}]
                },

       
             ])

    recent_summary_anodizing_overhead = recent_summary_initial.filter(Accountno=5750105) | recent_summary_initial.filter(Accountno=5750350) |\
                             recent_summary_initial.filter(Accountno=5750410) | recent_summary_initial.filter(Accountno=5750120) |\
                             recent_summary_initial.filter(Accountno=5750310) | recent_summary_initial.filter(Accountno=5750109) |\
                             recent_summary_initial.filter(Accountno=5750126) | recent_summary_initial.filter(Accountno=5750352) |\
                             recent_summary_initial.filter(Accountno=5750211) | recent_summary_initial.filter(Accountno=5750900) |\
                             recent_summary_initial.filter(Accountno=5750351) | recent_summary_initial.filter(Accountno=5750356) |\
                             recent_summary_initial.filter(Accountno=5750357) | recent_summary_initial.filter(Accountno=5750364) |\
                             recent_summary_initial.filter(Accountno=5750112) | recent_summary_initial.filter(Accountno=5750230) |\
                             recent_summary_initial.filter(Accountno=5750321) | recent_summary_initial.filter(Accountno=5750610) |\
                             recent_summary_initial.filter(Accountno=5750705) | recent_summary_initial.filter(Accountno=5750800) |\
                             recent_summary_initial.filter(Accountno=5750806) | recent_summary_initial.filter(Accountno=5750210) |\
                             recent_summary_initial.filter(Accountno=5750210) | recent_summary_initial.filter(Accountno=5750702) |\
                             recent_summary_initial.filter(Accountno=5750510)
    recent_summary_overhead = recent_summary_anodizing_overhead.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_overhead = DataPool(
           series=
            [{'options': {
            'source': recent_summary_overhead},
                'terms': [{'Accountno': 'Accountno',
                'overhead expense': 'total'}]
                },

       
             ])
    #end past three month datatable

    def glname(gl_num):
        names = {
            '5750100':'Direct Labor Salaries (ANODIZING)', '5750115':'Health And Welfare (ANODIZING)', '5750103':'Overtime/Double Time (ANODIZING)', '5750108':'!W/C INS - Direct Labor (ANODIZING)',
            '5750125':'Payroll Taxes Direct Labor (ANODIZING)', '5750104':'Direct Labor Vacation (ANODIZING)', '5750111':'Union 401K (ANODIZING)', '5750102':'Direct Labor Incentives (ANODIZING)',
            '5750110':'Union Pension (ANODIZING)', '5750105':'Indirect Salaries Supervision (ANODIZING)', '5750350':'Maintenance & Repair (ANODIZING)', '5750410':'Equipment Rental (ANODIZING)',
            '5750120':'Hospitalization (ANODIZING)', '5750310':'Shop Supplies (ANODIZING)', '5750109':'!W/C INS - IND DIR LABOR (ANODIZING)', '5750126':'Payroll Taxes Indirect Labor (ANODIZING)',
            '5750352':'Racking Expense (ANODIZING)', '5750211':'Salesman Commissions (ANODIZING)', '5750900':'Depreciation Expense (ANODIZING)', '5750351':'Equipment Repair (ANODIZING)',
            '5750356':'Pump Repair (ANODIZING)', '5750357':'Motor Repair (ANODIZING)', '5750364':'Outside Mechanical (ANODIZING)', '5750112':'Labor Transfer In/(Out) (ANODIZING)',
            '5750230':'Computer Expense (ANODIZING)', '5750321':'Electrical Expense (ANODIZING)', '5750610':'Travel Expenses (ANODIZING)', '5750705':'Outside Anodizing (ANODIZING)',
            '5750800':'Hazardous Waste (ANODIZING)', '5750806':'Temporary Employees (ANODIZING)', '5750210':'Office Supplies (ANODIZING)', '5750702':'Non-Production Chemicals (ANODIZING)',
            '5750510':'Heat, Light & Power (ANODIZING)', '5750701':'Purchase Chemicals (ANODIZING)'
            }
        return names[gl_num]

    #start all time foundry datapool
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_anodizing_material = summary_initial.filter(Accountno=5750701)
    summary_material = summary_anodizing_material.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    material =  DataPool(
           series=
            [{'options': {
            'source': summary_material},
                'terms': [{'month': 'month',
                'material cost': 'total'}]
                },

       
             ])

    summary_anodizing_labor = summary_initial.filter(Accountno=5750100) | summary_initial.filter(Accountno=5750115) |\
                             summary_initial.filter(Accountno=5750103) | summary_initial.filter(Accountno=5750108) |\
                             summary_initial.filter(Accountno=5750125) | summary_initial.filter(Accountno=5750104) |\
                             summary_initial.filter(Accountno=5750111) | summary_initial.filter(Accountno=5750102) |\
                             summary_initial.filter(Accountno=5750110) 
    summary_labor = summary_anodizing_labor.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    labor =  DataPool(
           series=
            [{'options': {
            'source': summary_labor},
                'terms': [{'month': 'month',
                'labor expense': 'total'}]
                },

       
             ])

    summary_anodizing_overhead = summary_initial.filter(Accountno=5750105) | summary_initial.filter(Accountno=5750350) |\
                             summary_initial.filter(Accountno=5750410) | summary_initial.filter(Accountno=5750120) |\
                             summary_initial.filter(Accountno=5750310) | summary_initial.filter(Accountno=5750109) |\
                             summary_initial.filter(Accountno=5750126) | summary_initial.filter(Accountno=5750352) |\
                             summary_initial.filter(Accountno=5750211) | summary_initial.filter(Accountno=5750900) |\
                             summary_initial.filter(Accountno=5750351) | summary_initial.filter(Accountno=5750356) |\
                             summary_initial.filter(Accountno=5750357) | summary_initial.filter(Accountno=5750364) |\
                             summary_initial.filter(Accountno=5750112) | summary_initial.filter(Accountno=5750230) |\
                             summary_initial.filter(Accountno=5750321) | summary_initial.filter(Accountno=5750610) |\
                             summary_initial.filter(Accountno=5750705) | summary_initial.filter(Accountno=5750800) |\
                             summary_initial.filter(Accountno=5750806) | summary_initial.filter(Accountno=5750210) |\
                             summary_initial.filter(Accountno=5750210) | summary_initial.filter(Accountno=5750702) |\
                             summary_initial.filter(Accountno=5750510)
    summary_overhead = summary_anodizing_overhead.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    overhead = DataPool(
           series=
            [{'options': {
            'source': summary_overhead},
                'terms': [{'month': 'month',
                'overhead expense': 'total'}]
                },

       
             ])
    #end all time datapool

    #start past three months foundry chart
    cht10 = Chart(
            datasource = recent_material,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Material Cost Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))  

    cht11 = Chart(
            datasource = recent_material,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Material Cost Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht12 = Chart(
            datasource = recent_material,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Material Cost Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht13 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Anodizing Labor Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht14 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Anodizing Labor Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht15 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Anodizing Labor Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht16 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Anodizing Overhead Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht17 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Anodizing Overhead Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht18 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Anodizing Overhead Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = material,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Material Cost Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = material,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Material Cost Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = material,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'material cost']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Material Cost Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Labor Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Labor Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Labor Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht7 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Overhead Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht8 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Overhead Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht9 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Anodizing Overhead Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end all time sales chart
    response = get_value(request.user.id)
    return render(request,'anodizingchart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18],'response':response})


#start customize shipping chart labor

def is_valid_queryparam_shipping2(param):
    return param != '' and param is not None


def filter_shipping2(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_labor = summary_initial.filter(Accountno=5800100) | summary_initial.filter(Accountno=5800115) |\
                             summary_initial.filter(Accountno=5800103) | summary_initial.filter(Accountno=5800108) |\
                             summary_initial.filter(Accountno=5800125) | summary_initial.filter(Accountno=5800104) |\
                             summary_initial.filter(Accountno=5800111) | summary_initial.filter(Accountno=5800102) |\
                             summary_initial.filter(Accountno=5800110)
    qs = summary_shipping_labor.order_by('Transdate')
    categories = ShippingLabor.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_shipping2(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_shipping2(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_shipping2(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_shipping2(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_labor = summary_initial.filter(Accountno=5800100) | summary_initial.filter(Accountno=5800115) |\
                             summary_initial.filter(Accountno=5800103) | summary_initial.filter(Accountno=5800108) |\
                             summary_initial.filter(Accountno=5800125) | summary_initial.filter(Accountno=5800104) |\
                             summary_initial.filter(Accountno=5800111) | summary_initial.filter(Accountno=5800102) |\
                             summary_initial.filter(Accountno=5800110)
    return summary_shipping_labor[int(offset): int(offset) + int(limit)]


def is_there_more_data_shipping2(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_labor = summary_initial.filter(Accountno=5800100) | summary_initial.filter(Accountno=5800115) |\
                             summary_initial.filter(Accountno=5800103) | summary_initial.filter(Accountno=5800108) |\
                             summary_initial.filter(Accountno=5800125) | summary_initial.filter(Accountno=5800104) |\
                             summary_initial.filter(Accountno=5800111) | summary_initial.filter(Accountno=5800102) |\
                             summary_initial.filter(Accountno=5800110)
    if int(offset) > summary_shipping_labor.count():
        return False
    return True


def BootstrapFilterView_shipping2(request):
    qs = filter_shipping2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': ShippingLabor.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_shipping2.html", context)

#end customize shipping chart labor

#start customize shipping chart overhead

def is_valid_queryparam_shipping3(param):
    return param != '' and param is not None


def filter_shipping3(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_overhead = summary_initial.filter(Accountno=5800105) | summary_initial.filter(Accountno=5800761) |\
                             summary_initial.filter(Accountno=5800845) | summary_initial.filter(Accountno=5800120) |\
                             summary_initial.filter(Accountno=5800760) | summary_initial.filter(Accountno=5800109) |\
                             summary_initial.filter(Accountno=5800762) | summary_initial.filter(Accountno=5800310) |\
                             summary_initial.filter(Accountno=5800126) | summary_initial.filter(Accountno=5800352) |\
                             summary_initial.filter(Accountno=5800350) | summary_initial.filter(Accountno=5800410) |\
                             summary_initial.filter(Accountno=5800889) | summary_initial.filter(Accountno=5800112) |\
                             summary_initial.filter(Accountno=5800210) | summary_initial.filter(Accountno=5800311) |\
                             summary_initial.filter(Accountno=5800321) | summary_initial.filter(Accountno=5800364) |\
                             summary_initial.filter(Accountno=5800351) | summary_initial.filter(Accountno=5800357) |\
                             summary_initial.filter(Accountno=5800806) | summary_initial.filter(Accountno=5800220) |\
                             summary_initial.filter(Accountno=5800320)
    qs = summary_shipping_overhead.order_by('Transdate')
    categories = ShippingOverhead.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')
    if is_valid_queryparam_shipping3(date_min):
        qs = qs.filter(Transdate__gte=date_min)

    if is_valid_queryparam_shipping3(date_max):
        qs = qs.filter(Transdate__lt=date_max)

    if is_valid_queryparam_shipping3(category) and category != 'Choose...':
        qs = qs.filter(Accountno=category)

    return qs


def infinite_filter_shipping3(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_overhead = summary_initial.filter(Accountno=5800105) | summary_initial.filter(Accountno=5800761) |\
                             summary_initial.filter(Accountno=5800845) | summary_initial.filter(Accountno=5800120) |\
                             summary_initial.filter(Accountno=5800760) | summary_initial.filter(Accountno=5800109) |\
                             summary_initial.filter(Accountno=5800762) | summary_initial.filter(Accountno=5800310) |\
                             summary_initial.filter(Accountno=5800126) | summary_initial.filter(Accountno=5800352) |\
                             summary_initial.filter(Accountno=5800350) | summary_initial.filter(Accountno=5800410) |\
                             summary_initial.filter(Accountno=5800889) | summary_initial.filter(Accountno=5800112) |\
                             summary_initial.filter(Accountno=5800210) | summary_initial.filter(Accountno=5800311) |\
                             summary_initial.filter(Accountno=5800321) | summary_initial.filter(Accountno=5800364) |\
                             summary_initial.filter(Accountno=5800351) | summary_initial.filter(Accountno=5800357) |\
                             summary_initial.filter(Accountno=5800806) | summary_initial.filter(Accountno=5800220) |\
                             summary_initial.filter(Accountno=5800320)
    return summary_shipping_overhead[int(offset): int(offset) + int(limit)]


def is_there_more_data_shipping3(request):
    offset = request.GET.get('offset')
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_overhead = summary_initial.filter(Accountno=5800105) | summary_initial.filter(Accountno=5800761) |\
                             summary_initial.filter(Accountno=5800845) | summary_initial.filter(Accountno=5800120) |\
                             summary_initial.filter(Accountno=5800760) | summary_initial.filter(Accountno=5800109) |\
                             summary_initial.filter(Accountno=5800762) | summary_initial.filter(Accountno=5800310) |\
                             summary_initial.filter(Accountno=5800126) | summary_initial.filter(Accountno=5800352) |\
                             summary_initial.filter(Accountno=5800350) | summary_initial.filter(Accountno=5800410) |\
                             summary_initial.filter(Accountno=5800889) | summary_initial.filter(Accountno=5800112) |\
                             summary_initial.filter(Accountno=5800210) | summary_initial.filter(Accountno=5800311) |\
                             summary_initial.filter(Accountno=5800321) | summary_initial.filter(Accountno=5800364) |\
                             summary_initial.filter(Accountno=5800351) | summary_initial.filter(Accountno=5800357) |\
                             summary_initial.filter(Accountno=5800806) | summary_initial.filter(Accountno=5800220) |\
                             summary_initial.filter(Accountno=5800320)
    if int(offset) > summary_shipping_overhead.count():
        return False
    return True


def BootstrapFilterView_shipping3(request):
    qs = filter_shipping2(request)
    response = get_value(request.user.id)
    context = {
        'queryset': qs,
        'categories': ShippingOverhead.objects.all(),
        'response':response
    }
    return render(request, "bootstrap_form_shipping3.html", context)

#end customize shipping chart overhead

@login_required
def shipping_chart(request):
    #start past three month extrusion datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary_initial = GeneralReport.objects.filter(Transdate__range=[startdate, enddate]).filter(Transamnt__gt=0)

    recent_summary_shipping_total = recent_summary_initial.filter(Accountno__gte = 5800000) & recent_summary_initial.filter(Accountno__lt = 5801000)
    recent_summary_total = recent_summary_shipping_total.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_total =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_total},
                'terms': [{'Accountno': 'Accountno',
                'total expense': 'total'}]
                },

       
             ])
    
    recent_summary_shipping_labor = recent_summary_initial.filter(Accountno=5800100) | recent_summary_initial.filter(Accountno=5800115) |\
                             recent_summary_initial.filter(Accountno=5800103) | recent_summary_initial.filter(Accountno=5800108) |\
                             recent_summary_initial.filter(Accountno=5800125) | recent_summary_initial.filter(Accountno=5800104) |\
                             recent_summary_initial.filter(Accountno=5800111) | recent_summary_initial.filter(Accountno=5800102) |\
                             recent_summary_initial.filter(Accountno=5800110)
    recent_summary_labor = recent_summary_shipping_labor.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_labor =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_labor},
                'terms': [{'Accountno': 'Accountno',
                'labor expense': 'total'}]
                },

       
             ])

    recent_summary_shipping_overhead = recent_summary_initial.filter(Accountno=5800105) | recent_summary_initial.filter(Accountno=5800761) |\
                             recent_summary_initial.filter(Accountno=5800845) | recent_summary_initial.filter(Accountno=5800120) |\
                             recent_summary_initial.filter(Accountno=5800760) | recent_summary_initial.filter(Accountno=5800109) |\
                             recent_summary_initial.filter(Accountno=5800762) | recent_summary_initial.filter(Accountno=5800310) |\
                             recent_summary_initial.filter(Accountno=5800126) | recent_summary_initial.filter(Accountno=5800352) |\
                             recent_summary_initial.filter(Accountno=5800350) | recent_summary_initial.filter(Accountno=5800410) |\
                             recent_summary_initial.filter(Accountno=5800889) | recent_summary_initial.filter(Accountno=5800112) |\
                             recent_summary_initial.filter(Accountno=5800210) | recent_summary_initial.filter(Accountno=5800311) |\
                             recent_summary_initial.filter(Accountno=5800321) | recent_summary_initial.filter(Accountno=5800364) |\
                             recent_summary_initial.filter(Accountno=5800351) | recent_summary_initial.filter(Accountno=5800357) |\
                             recent_summary_initial.filter(Accountno=5800806) | recent_summary_initial.filter(Accountno=5800220) |\
                             recent_summary_initial.filter(Accountno=5800320)
    recent_summary_overhead = recent_summary_shipping_overhead.values('Accountno').annotate(total=Round(Sum('Transamnt'))).order_by()
    recent_overhead = DataPool(
           series=
            [{'options': {
            'source': recent_summary_overhead},
                'terms': [{'Accountno': 'Accountno',
                'overhead expense': 'total'}]
                },

       
             ])
    #end past three month datatable

    def glname(gl_num):
        names = {
            '5800100':'Direct Labor Salaries (SHIPPING)', '5800115':'Health And Welfare (SHIPPING)', '5800103':'Overtime/Double Time (SHIPPING)', '5800108':'!W/C INS - Direct Labor (SHIPPING)',
            '5800125':'Payroll Taxes Direct Labor (SHIPPING)', '5800104':'Direct Labor Vacation (SHIPPING)', '5800111':'Union 401K (SHIPPING)', '5800102':'Direct Labor Incentives (SHIPPING)',
            '5800110':'Union Pension (SHIPPING)', '5800105':'Indirect Salaries Supervision (SHIPPING)', '5800761':'Lumber & Packing (SHIPPING)', '5800845':'Truck And Auto (SHIPPING)',
            '5800120':'Hospitalization (SHIPPING)', '5800760':'Corrugated & Paper (SHIPPING)', '5800109':'!W/C INS - IND DIR LABOR (SHIPPING)', '5800762':'Steel Strapping & Tape (SHIPPING)',
            '5800310':'Shop Supplies (SHIPPING)', '5800126':'Payroll Taxes Indirect Labor (SHIPPING)', '5800352':'Lift Truck Repairs (SHIPPING)', '5800350':'Maintenance & Repairs (SHIPPING)',
            '5800410':'Equipment Rental (SHIPPING)', '5800889':'Placement Fee (SHIPPING)', '5800112':'Labor Transfer In/(Out) (SHIPPING)', '5800210':'Office Supplies (SHIPPING)',
            '5800311':'Saw Blades (SHIPPING)', '5800321':'Electrical Expense (SHIPPING)', '5800364':'5800364', '5800351':'Crane Repair (SHIPPING)', '5800357':'Motor Repair (SHIPPING)',
            '5800806':'Temporary Employees (SHIPPING)', '5800220':'Furniture & Fixtures Expense (SHIPPING)', '5800320':'Hardware And Mill (SHIPPING)'
            }
        return names[gl_num]

    #start all time foundry datapool
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_shipping_total = summary_initial.filter(Accountno__gte = 5800000) & summary_initial.filter(Accountno__lt = 5801000)
    summary_total = summary_shipping_total.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    total =  DataPool(
           series=
            [{'options': {
            'source': summary_total},
                'terms': [{'month': 'month',
                'total expense': 'total'}]
                },

       
             ])

    summary_shipping_labor = summary_initial.filter(Accountno=5800100) | summary_initial.filter(Accountno=5800115) |\
                             summary_initial.filter(Accountno=5800103) | summary_initial.filter(Accountno=5800108) |\
                             summary_initial.filter(Accountno=5800125) | summary_initial.filter(Accountno=5800104) |\
                             summary_initial.filter(Accountno=5800111) | summary_initial.filter(Accountno=5800102) |\
                             summary_initial.filter(Accountno=5800110)
    summary_labor = summary_shipping_labor.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    labor =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': summary_labor},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'month': 'month',
                'labor expense': 'total'}]
                },

       
             ])

    summary_shipping_overhead = summary_initial.filter(Accountno=5800105) | summary_initial.filter(Accountno=5800761) |\
                             summary_initial.filter(Accountno=5800845) | summary_initial.filter(Accountno=5800120) |\
                             summary_initial.filter(Accountno=5800760) | summary_initial.filter(Accountno=5800109) |\
                             summary_initial.filter(Accountno=5800762) | summary_initial.filter(Accountno=5800310) |\
                             summary_initial.filter(Accountno=5800126) | summary_initial.filter(Accountno=5800352) |\
                             summary_initial.filter(Accountno=5800350) | summary_initial.filter(Accountno=5800410) |\
                             summary_initial.filter(Accountno=5800889) | summary_initial.filter(Accountno=5800112) |\
                             summary_initial.filter(Accountno=5800210) | summary_initial.filter(Accountno=5800311) |\
                             summary_initial.filter(Accountno=5800321) | summary_initial.filter(Accountno=5800364) |\
                             summary_initial.filter(Accountno=5800351) | summary_initial.filter(Accountno=5800357) |\
                             summary_initial.filter(Accountno=5800806) | summary_initial.filter(Accountno=5800220) |\
                             summary_initial.filter(Accountno=5800320)
    summary_overhead = summary_shipping_overhead.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
    overhead = DataPool(
           series=
            [{'options': {
            'source': summary_overhead},
                'terms': [{'month': 'month',
                'overhead expense': 'total'}]
                },

       
             ])
    #end all time datapool

    #start past three months foundry chart
    cht10 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Total Cost Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))  

    cht11 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Total Cost Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht12 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Total Cost Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht13 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Shipping Labor Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht14 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Shipping Labor Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht15 = Chart(
            datasource = recent_labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'labor expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Shipping Labor Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht16 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Shipping Overhead Expense Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht17 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Shipping Overhead Expense Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht18 = Chart(
            datasource = recent_overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Accountno': [
                    'overhead expense']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Shipping Overhead Expense Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Total Cost Amount All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Total Cost Amount All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Total Cost Amount All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Labor Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Labor Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = labor,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'labor expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Labor Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht7 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Overhead Expense Amounts All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht8 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Overhead Expense Amounts All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht9 = Chart(
            datasource = overhead,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'overhead expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Shipping Overhead Expense Amounts All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end all time sales chart
    response = get_value(request.user.id)
    return render(request,'shippingchart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18],'response':response})

@login_required
def paint_chart(request):
    #start past three month extrusion datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary_initial = PurchaseReport.objects.filter(Datepromised__range=[startdate, enddate]).filter(Line_Amount__gt=0)

    recent_summary_paint_total = recent_summary_initial.filter(Vendor_Name__contains = 'POWDER')
    recent_summary_total = recent_summary_paint_total.values('GL_Accountno').annotate(total=Round(Sum('Line_Amount'))).order_by()
    recent_total =  DataPool(
           series=
            [{'options': {
            'source': recent_summary_total},
                'terms': [{'Accountno': 'GL_Accountno',
                'total expense': 'total'}]
                },

       
             ])
    #end past three month datatable

    #start all time foundry datapool
    summary_initial = PurchaseReport.objects.filter(Line_Amount__gt=0)
    summary_paint_total = summary_initial.filter(Vendor_Name__contains = 'POWDER')
    summary_total = summary_paint_total.annotate(month=TruncMonth('Datepromised')).values('month').annotate(total=Round(Sum('Line_Amount'))).order_by()
    total =  DataPool(
           series=
            [{'options': {
            'source': summary_total},
                'terms': [{'month': 'month',
                'total expense': 'total'}]
                },

       
             ])
    #end all time datapool

    #start past three months foundry chart
    cht = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Paint Total Cost Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Paint Total Cost Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = recent_total,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'Accountno': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Paint Total Cost Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Account Name'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end past three months sales chart
    
    #start all time sales chart
    cht4 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Paint Total Cost Amount All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht5 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Paint Total Cost Amount All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht6 = Chart(
            datasource = total,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total expense']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Paint Total Cost Amount All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Cost'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end all time sales chart
    response = get_value(request.user.id)
    return render(request,'paintchart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6],'response':response})

@login_required
def sales_chart(request):

    def monthlyname(monthly_num):
        names = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
                 }
        return names[monthly_num]         

    def monthname(month_num):
        names = {
                1701: 'Jan 2017', 1702: 'Feb 2017', 1703: 'Mar 2017', 1704: 'Apr 2017', 1705: 'May 2017', 1706: 'Jun 2017',
                1707: 'Jul 2017', 1708: 'Aug 2017', 1709: 'Sep 2017', 1710: 'Oct 2017', 1711: 'Nov 2017', 1712: 'Dec 2017',
                1801: 'Jan 2018', 1802: 'Feb 2018', 1803: 'Mar 2018', 1804: 'Apr 2018', 1805: 'May 2018', 1806: 'Jun 2018',
                1807: 'Jul 2018', 1808: 'Aug 2018', 1809: 'Sep 2018', 1810: 'Oct 2018', 1811: 'Nov 2018', 1812: 'Dec 2018',
                1901: 'Jan 2019', 1902: 'Feb 2019', 1903: 'Mar 2019', 1904: 'Apr 2019', 1905: 'May 2019', 1906: 'Jun 2019',
                1907: 'Jul 2019', 1908: 'Aug 2019', 1909: 'Sep 2019', 1910: 'Oct 2019', 1911: 'Nov 2019', 1912: 'Dec 2019',
                2001: 'Jan 2020', 2002: 'Feb 2020', 2003: 'Mar 2020',
                 }
        return names[month_num]
    
    #start past three month sales datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary = SalesReport.objects.filter(Invoicedate__range=[startdate, enddate]).annotate(month=TruncMonth('Invoicedate')).values('month').annotate(total=Round(Sum('Calc_Price'))).order_by()
    recent_sales =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_summary},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'month': 'month',
                'sales': 'total'}]
                },

       
             ])
    recent_company = SalesReport.objects.filter(Invoicedate__range=[startdate, enddate]).values('Companyname').annotate(total=Round(Sum('Calc_Price'))).order_by()
    recent_customer =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': recent_company},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'Companyname': 'Companyname',
                'sales': 'total'}]
                },

       
             ])

    recent_rsm = SalesReport.objects.filter(Invoicedate__range=[startdate, enddate]).values('RSM_name').annotate(total=Round(Sum('Calc_Price'))).order_by()
    recent_rsmname = DataPool(
           series=
            [{'options': {
            'source': recent_rsm},
                'terms': [{'RSM_name': 'RSM_name',
                'sales': 'total'}]
                },

       
             ])
    #end past three month datatable
    
    #start all time sales datapool
    summary = SalesReport.objects.annotate(month=TruncMonth('Invoicedate')).values('month').annotate(total=Round(Sum('Calc_Price'))).order_by()
    sales =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': summary},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'month': 'month',
                'sales': 'total'}]
                },

       
             ])
    
    company = SalesReport.objects.values('Companyname').annotate(total=Round(Sum('Calc_Price'))).order_by()
    customer =  DataPool(
           series=
            [{'options': {
            #    'source': SalesReport.objects.all()},
            'source': company},
            #'source': SalesReport.objects.filter(sales__lte=10.00)},
                'terms': [{'Companyname': 'Companyname',
                'sales': 'total'}]
                },

       
             ])
    rsm = SalesReport.objects.values('RSM_name').annotate(total=Round(Sum('Calc_Price'))).order_by()
    rsmname = DataPool(
           series=
            [{'options': {
            'source': rsm},
                'terms': [{'RSM_name': 'RSM_name',
                'sales': 'total'}]
                },

       
             ])
    #end all time sales datapool

    #start compare sales datapool
    compare_sales =  DataPool(
           series=
            [{'options': {
            'source': SalesMonthly},
                'terms': [{'month': 'month',
                '2017 sales': 'seventeen',
                '2018 sales': 'eighteen',
                '2019 sales': 'nineteen'
                           }]
                },

       
             ])
    
    
    compare_customer = DataPool(
           series=
            [{'options': {
            'source': SalesCustomer},
                'terms': [{'month': 'month',
                'WABASH': 'top1',
                'U-HAUL': 'top2',
                'MORGAN': 'top3'
                           }]
                },

       
             ])
    
    compare_manager = DataPool(
           series=
            [{'options': {
            'source': SalesManager},
                'terms': [{'month': 'month',
                'jdevincentis': 'top1',
                'kheston': 'top2',
                'cpalmer': 'top3'
                           }]
                },

       
             ])

    #end compare sales datapool

    
    #start past three months sales chart
    cht10 = Chart(
            datasource = recent_sales,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'sales']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Sales Amounts Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht11 = Chart(
            datasource = recent_sales,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht12 = Chart(
            datasource = recent_sales,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht13 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Companyname': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Customer Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Customer Name'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht14 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Companyname': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Customer Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Customer Name'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht15 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Companyname': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Customer Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Customer Name'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    cht16 = Chart(
            datasource = recent_rsmname,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'RSM_name': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Sales Manager Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Sales Manager'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht17 = Chart(
            datasource = recent_rsmname,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'RSM_name': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Sales Manager Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Sales Manager'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht18 = Chart(
            datasource = recent_rsmname,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'RSM_name': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Sales Manager Over Past Three Months- Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Sales Manager'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = sales,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'sales']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Sales Amounts Over Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = sales,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts Over Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = sales,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts Over Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = customer,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Companyname': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Customer - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Customer Name'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = customer,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Companyname': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Customer - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Customer Name'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = customer,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Companyname': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Customer - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Customer Name'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    cht7 = Chart(
            datasource = rsmname,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'RSM_name': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Sales Manager - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Sales Manager'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht8 = Chart(
            datasource = rsmname,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'RSM_name': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Sales Manager - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Sales Manager'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht9 = Chart(
            datasource = rsmname,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'RSM_name': [
                    'sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Sales Amounts of each Sales Manager - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Sales Manager'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    #end all time sales chart
    
    #start compare sales chart
    cht19 = Chart(
            datasource = compare_sales,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    '2017 sales', '2018 sales', '2019 sales']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Three Year Sales Monthly Compare - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, monthlyname, False))

    cht20 = Chart(
            datasource = compare_customer,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'WABASH', 'U-HAUL', 'MORGAN']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Three Year Top3 Sales Customer Compare - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, monthname, False))

    cht21 = Chart(
            datasource = compare_manager,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'jdevincentis', 'kheston', 'cpalmer']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Three Year Top3 Sales Manager Compare - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Sales'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, monthname, False))
    #end compare sales chart
    response = get_value(request.user.id)
    return render(request,'saleschart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18, cht19, cht20, cht21],'response':response})

@login_required
def purchase_chart(request):

    def monthlyname(monthly_num):
        names = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
                 }
        return names[monthly_num]         

    def monthname(month_num):
        names = {
                1701: 'Jan 2017', 1702: 'Feb 2017', 1703: 'Mar 2017', 1704: 'Apr 2017', 1705: 'May 2017', 1706: 'Jun 2017',
                1707: 'Jul 2017', 1708: 'Aug 2017', 1709: 'Sep 2017', 1710: 'Oct 2017', 1711: 'Nov 2017', 1712: 'Dec 2017',
                1801: 'Jan 2018', 1802: 'Feb 2018', 1803: 'Mar 2018', 1804: 'Apr 2018', 1805: 'May 2018', 1806: 'Jun 2018',
                1807: 'Jul 2018', 1808: 'Aug 2018', 1809: 'Sep 2018', 1810: 'Oct 2018', 1811: 'Nov 2018', 1812: 'Dec 2018',
                1901: 'Jan 2019', 1902: 'Feb 2019', 1903: 'Mar 2019', 1904: 'Apr 2019', 1905: 'May 2019', 1906: 'Jun 2019',
                1907: 'Jul 2019', 1908: 'Aug 2019', 1909: 'Sep 2019', 1910: 'Oct 2019', 1911: 'Nov 2019', 1912: 'Dec 2019',
                2001: 'Jan 2020', 2002: 'Feb 2020', 2003: 'Mar 2020',
                 }
        return names[month_num]

    def glname(gl_num):
        names = {
                '1500110': 'BUILDING IMPROVEMENTS (CAPITAL EXPENSE AND MISC.)', '1500115': 'BUILDING IMPROVEMENTS - ANODIZING (CAPITAL EXPENSE AND MISC.)',
                '1500300': 'M & E  - DIES (CAPITAL EXPENSE AND MISC.)', '1500310': 'M & E  - DIE TOOLING (CAPITAL EXPENSE AND MISC.)',
                '1500315': 'FABRICATION DIES & TOOLING (CAPITAL EXPENSE AND MISC.)', '1500320': 'M & E  - SHAPES (CAPITAL EXPENSE AND MISC.)',
                '1500323': 'M & E  - FOUNDRY (CAPITAL EXPENSE AND MISC.)', '1500325': 'M & E DANIELI PRESS (CAPITAL EXPENSE AND MISC.)',
                '1500330': 'ANODIZING LINE (CAPITAL EXPENSE AND MISC.)', '1500350': 'ELECTRODE (CAPITAL EXPENSE AND MISC.)',
                '1500400': 'COMPUTER EQUIPMENT (CAPITAL EXPENSE AND MISC.)', '4105204': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4105206': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4106654': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4110610': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4110621': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4110744': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4110971': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4111259': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4111351': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4111357': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4111629': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4111631': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4111875': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4112444': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4112487': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4113189': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4113327': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4113382': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4113388': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4113390': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4113396': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4113404': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4113413': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4113415': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4113421': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4113423': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4113907': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4114027': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4114271': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4114863': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4115000': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4115165': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4115287': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4115523': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4115649': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4115661': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4115983': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4115989': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4115991': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4115993': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4115995': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4116001': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4116007': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4116009': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4116011': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4116015': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4116019': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4116122': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4116155': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4116809': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4120725': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4120741': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4120773': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4120789': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4120870': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4120874': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4121196': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4121618': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4121933': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4121937': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4122019': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4122021': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4122031': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4122754': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4122776': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4123155': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4123639': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4123975': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4123979': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4124045': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4124131': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4125349': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4125353': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4125357': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4125359': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4125361': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4125699': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4125815': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4126617': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4126907': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4127334': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4127346': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4128187': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4128189': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4128896': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4128900': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4128902': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4128908': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4128910': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4128912': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4128914': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4128920': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4129022': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4129998': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4130181': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4130183': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4130185': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4130229': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4130261': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4130625': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4130901': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4131134': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4131218': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4131219': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4131664': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4131666': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4131668': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4131672': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4132160': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4132702': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4132706': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4133720': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4133889': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4133891': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4133893': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4133895': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4133897': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4133899': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4135131': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4135133': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4135154': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4135870': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4136630': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4137176': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4137178': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4137824': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4137826': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4137832': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4139166': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4139170': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4139178': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4139180': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4139878': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4140869': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4141601': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4141607': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4141650': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4141654': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4141992': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4142281': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4142659': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4142661': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4142663': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4142731': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4143071': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4143305': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4143637': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4143639': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4143641': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4143645': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4143647': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4143649': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4144388': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4144414': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4145286': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4145533': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4145535': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4145537': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4145539': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4146283': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4146285': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4146510': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4146512': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4146758': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4147468': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4147632': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4148323': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4148325': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4149641': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4149643': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4149647': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4149923': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4149925': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4150726': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4150941': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4151663': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4151710': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4152598': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4152958': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4153891': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4155928': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4155972': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4156342': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4156346': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4156617': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4157493': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4157495': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4158163': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4158165': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4159362': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4159370': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4159372': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4159374': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4159376': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4159382': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4159384': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4159386': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4159714': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4160207': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4160492': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4161219': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4161225': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4161227': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4161229': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4161593': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4161595': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4162781': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4162783': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4162785': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4162789': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4162976': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4163041': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4163043': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4163045': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4164186': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4164206': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '416459': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4165213': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4165388': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4165459': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4166415': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4166761': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4166763': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4167003': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4168113': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4168630': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4168817': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4169687': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4170032': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4170197': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4170199': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171133': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4171137': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171139': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4171147': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171149': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4171722': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171775': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4171777': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171779': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4171800': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171802': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4171804': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4171806': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4172101': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4172103': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4172320': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4172322': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4172324': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4172328': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4172469': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4172614': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4172616': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4172618': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4173307': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4173311': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4173233': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4173307': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4173309': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4173311': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4173656': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4173668': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4173674': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4173676': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4173678': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4174044': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4174046': 'OUTSOURCE PROCESSING (OUTSOOURCE)',
                '4174048': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '4200100': 'Cos Oem',
                '430625': 'OUTSOURCE PROCESSING (OUTSOOURCE)', '510000': 'Direct Labor Salaries (FOUNDRY)',
                '5100210': 'Office Supplies (FOUNDRY)', '5100310': 'Shop Supplies (FOUNDRY)', '5100311': 'Saw Blades Expense (FOUNDRY)', '5100312': 'Uniform Expense (FOUNDRY)',
                '5100313': 'Wagstaff Supplies & Equip (FOUNDRY)', '5100315': 'Filtration Supplies (FOUNDRY)', '5100316': 'Lubricants (FOUNDRY)', '5100317': 'Mach & Fabtn-O/S (FOUNDRY)',
                '5100318': '5100318', '5100319': 'Thermocouple Tubes (FOUNDRY)', '5100320': 'Hardware And Mill (FOUNDRY)', '5100321': 'Electrical Expense (FOUNDRY)',
                '5100322': 'Gloves (FOUNDRY)', '5100350': 'Maintenance & Repair (FOUNDRY)', '5100351': 'Crane Repairs (FOUNDRY)', '5100352': 'Lift Truck Repairs (FOUNDRY)',
                '5100355': 'Gasoline (FOUNDRY)', '5100359': 'Argon (FOUNDRY)', '5100360': 'Oven Repairs (FOUNDRY)', '5100363': 'Refractory Repairs (FOUNDRY)', '5100364': 'Outside Mechanical (FOUNDRY)',
                '5100410': 'Equipment Rental (FOUNDRY)', '5100710': 'Purchases Log & Billet (FOUNDRY)', '5100711': 'Purchases Copper (FOUNDRY)',
                '5100714': 'Purchases Miscellaneous (FOUNDRY)', '5100715': 'Purchases Magnesium (FOUNDRY)', '5100716': 'Purchases Pig (FOUNDRY)', '5100717': 'Purchases Scrap (FOUNDRY)',
                '5100719': 'Purchases Silicon (FOUNDRY)', '5100720': 'Purchases Titaniun & Tibor (FOUNDRY)', '5100725': 'Purchases Titaniun & Tibor (FOUNDRY)', '5100761': 'Freight Out - Finished Product (FOUNDRY)', '5100762': 'Freight Out - Finished Product (FOUNDRY)', '5300310': 'Shop Supplies (DIE CORRECTION)',
                '5300350': 'Maintenance & Repair (DIE CORRECTION)', '5300352': 'Lift Truck Expense (DIE CORRECTION)', '5300701': 'Chemicals (DIE CORRECTION)',
                '540000': '540000', '5400310': 'Shop Supplies (EXTRUSION)', '5400311': 'Saw Blades (EXTRUSION)', '5400320': 'Hardware And Mill (EXTRUSION)',
                '5400321': 'Electrical Expense (EXTRUSION)', '5400322': 'Gloves & Personal Equip (EXTRUSION)', '5400331': 'Filters (EXTRUSION)', '5400332': 'Nitrogen (EXTRUSION)', '5400333': 'Lubricants (EXTRUSION)',
                '5400334': 'Oil & Fluids (EXTRUSION)', '5400350': 'Maintenance & Repairs (EXTRUSION)', '5400351': 'Crane Expense (EXTRUSION)', '5400352': 'Lift Truck Expense (EXTRUSION)', '5400354': 'Quality Control (EXTRUSION)',
                '5400356': 'Pump Repair (EXTRUSION)', '5400357': 'Motor Repair (EXTRUSION)', '5400358': 'Billet Heater Repairs (EXTRUSION)', '5400359': 'Handling Equipment Repairs (EXTRUSION)',
                '5400364': 'Outside Mechanical (EXTRUSION)', '5400365': 'Outside Electrical (EXTRUSION)', '5400410': 'Equipment Rental (EXTRUSION)', '5400762': 'STRAPPING,PACKAGING,EXTRUSION (EXTRUSION)',
                '5650309': 'Tooling Expense (FABRICATION)', '5650310': 'Shop Supplies (FABRICATION)', '5650311': 'Saw Blades (FABRICATION)', '5650320': 'Hardware And Mill (FABRICATION)', '5650350': 'Maintenance & Repairs (FABRICATION)',
                '5650352': 'Lift Truck Repairs (FABRICATION)', '5650702': 'Purchase Fabrication', '569205': '569205', '569405': '569405', '569501': '569501', '5700350': 'Maintenance & Repair (PAINTLINE)', '5700701': '5700701', '570073': '570073',
                '5750310': 'Shop Supplies (ANODIZING)', '5750350': 'Maintenance & Repair (ANODIZING)', '5750352': 'Racking Expense (ANODIZING)', '5750364': 'Outside Mechanical (ANODIZING)', '5750410': 'Equipment Rental (ANODIZING)',
                '5750701': 'Purchase Chemicals (ANODIZING)', '5750705': 'Outside Anodizing (ANODIZING)', '5800210': 'Office Supplies (SHIPPING)',
                '5800310': 'Shop Supplies (SHIPPING)', '5800321': 'Electrical Expense (SHIPPING)', '5800350': 'Maintenance & Repairs (SHIPPING)',
                '5800352': 'Lift Truck Repairs (SHIPPING)', '5800760': 'Corrugated & Paper (SHIPPING)', '5800761': 'Lumber & Packing (SHIPPING)',
                '5800762': 'Steel Strapping & Tape (SHIPPING)', '5800845': 'Truck And Auto (SHIPPING)', '5900175': 'Christmas Expense (GENERAL PLANT)',
                '5900210': 'Office Supplies (GENERAL PLANT)', '5900310': 'Shop Supplies (GENERAL PLANT)', '5900312': 'Uniform Expense (GENERAL PLANT)',
                '5900320': 'Hardware And Mill (GENERAL PLANT)', '5900321': 'Electrical Expense (GENERAL PLANT)', '5900350': 'Maintenance & Repairs (GENERAL PLANT)',
                '5900351': 'Crane Repair (GENERAL PLANT)', '5900352': 'Lift Truck Repairs (GENERAL PLANT)', '5900355': 'Gas And Oil (GENERAL PLANT)',
                '5900360': 'Oven Repairs (GENERAL PLANT)', '5900361': 'Safety (GENERAL PLANT)', '5900364': 'Outside Mechanical (GENERAL PLANT)', '5900410': 'Equipment Rental (GENERAL PLANT)',
                '5900800': 'Hazardous Waste (GENERAL PLANT)', '5900810': '!ENVIROMENTAL EXP (GENERAL PLANT)',
                '5900862': 'TRAINING (GENERAL PLANT)', '5950210': 'Office Supplies (QUALITY CONTROL)', '5950310': 'Shop Supplies (QUALITY CONTROL)', '5950320': 'Hardware And Mill (QUALITY CONTROL)',
                '5950321': 'CALIBRATION (QUALITY CONTROL)', '5950350': 'Maintenance & Repairs (QUALITY CONTROL)', '5950610': 'Travel Expenses (QUALITY CONTROL)',
                '6010175': 'Christmas Expense (OFFICE)', '6010210': 'Office Supplies (OFFICE)', '6010230': 'Computer Expense Shapes (OFFICE)', '6010330': 'Cleaning Expense (OFFICE)',
                '6010350': 'Maintenance & Repairs (OFFICE)', '6010611': 'Transportation-Airline-Office (OFFICE)', '6010805': 'Legal, Audit & Professional (OFFICE)', '6010806': 'Consulting/Temporary Personnel (OFFICE)',
                '6010810': 'Environmental Expense (OFFICE)', '6010875': 'Stationary & Printing Expense (OFFICE)', '6010888': 'Telephone/Fax/Cell-Office (OFFICE)', '6020210': 'Office Supplies (SALES) ',
                '6020851': 'Advertising (SALES)', '6070230': 'COMPUTER EXP (IT)', 'E': 'E'}
        return names[gl_num]

    
    #start past three month sales datapool
    enddate = datetime.today()
    startdate = enddate - timedelta(days=90)
    recent_summary = PurchaseReport.objects.filter(Datepromised__range=[startdate, enddate]).annotate(month=TruncMonth('Datepromised')).values('month').annotate(total=Round(Sum('Line_Amount'))).order_by()
    recent_purchase =  DataPool(
           series=
            [{'options': {
            'source': recent_summary},
                'terms': [{'month': 'month',
                'purchase': 'total'}]
                },

       
             ])

    recent_company = PurchaseReport.objects.filter(Datepromised__range=[startdate, enddate]).values('Vendor_Name').annotate(total=Round(Sum('Line_Amount'))).order_by()
    recent_customer =  DataPool(
           series=
            [{'options': {
            'source': recent_company},
                'terms': [{'Vendor_Name': 'Vendor_Name',
                'purchase': 'total'}]
                },

       
             ])

    recent_dep = PurchaseReport.objects.filter(Datepromised__range=[startdate, enddate]).values('GL_Accountno').annotate(total=Round(Sum('Line_Amount'))).order_by()
    recent_department = DataPool(
           series=
            [{'options': {
            'source': recent_dep},
                'terms': [{'department': 'GL_Accountno',
                'purchase': 'total'}]
                },

       
             ])
    #end past three month purchase datapool
    
    #start all month purchase datapool
    summary = PurchaseReport.objects.annotate(month=TruncMonth('Datepromised')).values('month').annotate(total=Round(Sum('Line_Amount'))).order_by()
    purchase =  DataPool(
           series=
            [{'options': {
            'source': summary},
                'terms': [{'month': 'month',
                'purchase': 'total'}]
                },

       
             ])

    company = PurchaseReport.objects.values('Vendor_Name').annotate(total=Round(Sum('Line_Amount'))).order_by()
    customer =  DataPool(
           series=
            [{'options': {
            'source': company},
                'terms': [{'Vendor_Name': 'Vendor_Name',
                'purchase': 'total'}]
                },

       
             ])

    dep = PurchaseReport.objects.values('GL_Accountno').annotate(total=Round(Sum('Line_Amount'))).order_by()
    department = DataPool(
           series=
            [{'options': {
            'source': dep},
                'terms': [{'department': 'GL_Accountno',
                'purchase': 'total'}]
                },

       
             ])
    #end all month purchase datapool

    #start compare purchase datapool
    compare_purchase =  DataPool(
           series=
            [{'options': {
            'source': PurchaseMonthly},
                'terms': [{'month': 'month',
                '2017 purchase': 'seventeen',
                '2018 purchase': 'eighteen',
                '2019 purchase': 'nineteen'
                           }]
                },

       
             ])

    
    compare_vendor =  DataPool(
           series=
            [{'options': {
            'source': PurchaseVendor},
                'terms': [{'month': 'month',
                'MARKOWITZ': 'top1',
                'ARIGATO METALS': 'top2',
                'TRIPLE M METAL': 'top3'
                           }]
                },

       
             ])

    
    compare_department =  DataPool(
           series=
            [{'options': {
            'source': PurchaseDepartment},
                'terms': [{'month': 'month',
                'ALUMINUM SCRAP': 'top1',
                'PRIME ALUMINUM': 'top2',
                'LOG AND BILLET': 'top3'
                           }]
                },

       
             ])
    
    #end compare purchase datapool
    
    #start past three months sales chart
    cht10 = Chart(
            datasource = recent_purchase,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'purchase']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht11 = Chart(
            datasource = recent_purchase,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht12 = Chart(
            datasource = recent_purchase,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht13 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Vendor_Name': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts from each Vendor Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Vendor Name'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht14 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Vendor_Name': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts from each Vendor Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Vendor Name'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht15 = Chart(
            datasource = recent_customer,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Vendor_Name': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Vendor Over Past Three Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Vendor Name'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    cht16 = Chart(
            datasource = recent_department,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'department': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Department Over Past Three Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Department'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht17 = Chart(
            datasource = recent_department,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'department': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Department Over Past Three Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Department'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht18 = Chart(
            datasource = recent_department,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'department': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Department Over Past Three Months- Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Department'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end past three months sales chart
    
    #start all time sales chart
    cht = Chart(
            datasource = purchase,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'purchase']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts Over Months - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = purchase,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts Over Months - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = purchase,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts Over Months - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month Number'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht4 = Chart(
            datasource = customer,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Vendor_Name': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts from each Vendor - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Vendor Name'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht5 = Chart(
            datasource = customer,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Vendor_Name': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts from each Vendor - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Vendor Name'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    
    cht6 = Chart(
            datasource = customer,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'Vendor_Name': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts from each Vendor - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Vendor Name'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    cht7 = Chart(
            datasource = department,
            series_options =
              [{'options':{
                  'type': 'column',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'department': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Department - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Department'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))

    cht8 = Chart(
            datasource = department,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'department': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Department - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Department'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    
    cht9 = Chart(
            datasource = department,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'department': [
                    'purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Purchase Amounts of each Department - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Department'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, glname, False))
    #end all time sales chart
    #start compare sales chart
    cht19 = Chart(
            datasource = compare_purchase,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    '2017 purchase', '2018 purchase', '2019 purchase']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Three Year Purchase Monthly Compare - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, monthlyname, False))

    cht20 = Chart(
            datasource = compare_vendor,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'MARKOWITZ', 'ARIGATO METALS', 'TRIPLE M METAL']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Three Year Top3 Purchase Vendor Compare - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, monthname, False))

    cht21 = Chart(
            datasource = compare_department,
            series_options =
              [{'options':{
                  'type': 'line',
                  'plotBorderWidth': 1,
                  'zoomType': 'xy',
                 
                  'legend':{
                      'enabled': True,
                  }},
                  
                'terms':{
                  'month': [
                    'ALUMINUM SCRAP', 'PRIME ALUMINUM', 'LOG AND BILLET']
                  }}],
    
            chart_options =
              {'title': {
                   'text': 'Three Year Top3 Purchase Item Compare - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Purchase'}},
                   
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}},
            x_sortf_mapf_mts=(None, monthname, False))
    #end compare sales chart
    response = get_value(request.user.id)
    return render(request,'purchasechart.html', 
        {'chart_list': [cht, cht2, cht3, cht4, cht5, cht6, cht7, cht8, cht9, cht10, cht11, cht12, cht13, cht14, cht15, cht16, cht17, cht18, cht19, cht20, cht21],'response':response})


@login_required
def show(request, order_id):
    order = Order.objects.filter(id=order_id)
    response = get_value(request.user.id)
    return render(request, 'show.html', {'order': order,'response':response})

@login_required
def showLine(request, line_id):
    line = Line.objects.filter(id=order_id)
    response = get_value(request.user.id)
    return render(request, 'showline.html', {'line': line,'response':response})

@login_required
def showPrice(request, price_id):
    price = Price.objects.filter(id=price_id)
    response = get_value(request.user.id)
    return render(request, 'showprice.html', {'price': price,'response':response})

@login_required
def showPurchase(request, purchase_id):
    purchase = Purchase.objects.filter(id=purchase_id)
    response = get_value(request.user.id)
    return render(request, 'showpurchase.html', {'purchase': purchase,'response':response})

@login_required
def new(request):
    if request.POST:
        form = OrderForm(request.POST)
        if form.is_valid():
            if form.save():
                return redirect('/orders', messages.success(request, 'Order was successfully created.', 'alert-success'))
            else:
                return redirect('/orders', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            print(form.errors)
            return redirect('/orders', messages.error(request, 'Form is not valid', 'alert-danger'))
    else:
        form = OrderForm()
        response = get_value(request.user.id)
        return render(request, 'new.html', {'form':form,'response':response})

@login_required
def newLine(request):
    if request.POST:
        line = OrderLine(request.POST)
        if line.is_valid():
            if line.save():
                return redirect('/order/indexline', messages.success(request, 'New Line was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexline', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexline', messages.error(request, 'Line is not valid', 'alert-danger'))
    else:
        line = OrderLine()
        response = get_value(request.user.id)
        return render(request, 'newline.html', {'line':line,'response':response})

@login_required
def edit(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.POST:
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            if form.save():
                return redirect('/orders', messages.success(request, 'Order was successfully updated.', 'alert-success'))
            else:
                return redirect('/orders', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            print(form.errors)
            return redirect('/orders', messages.error(request, 'Form is not valid', 'alert-danger'))
    else:
        form = OrderForm(instance=order)
        response = get_value(request.user.id)
        return render(request, 'edit.html', {'form':form,'response':response})

@login_required
def editLine(request, line_id):
    line = Line.objects.get(id=line_id)
    if request.POST:
        line = OrderLine(request.POST, instance=line)
        if line.is_valid():
            if line.save():
                return redirect('/order/indexline', messages.success(request, 'New Line was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexline', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexline', messages.error(request, 'Line is not valid', 'alert-danger'))
    else:
        line = OrderLine(instance=line)
        response = get_value(request.user.id)
        return render(request, 'editline.html', {'line':line,'response':response})
    
@login_required
def editPrice(request, price_id):
    price = Price.objects.get(id=price_id)
    if request.POST:
        price = PriceForm(request.POST, instance=price)
        if price.is_valid():
            if price.save():
                return redirect('/order/indexprice', messages.success(request, 'New Price was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexprice', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexprice', messages.error(request, 'Price is not valid', 'alert-danger'))
    else:
        price = PriceForm(instance=price)
        response = get_value(request.user.id)
        return render(request, 'editprice.html', {'price':price,'response':response})

@login_required
def destroy(request, order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    return redirect('/orders', messages.success(request, 'Order was successfully deleted.', 'alert-success'))

@login_required
def destroyLine(request, line_id):
    line = Line.objects.get(id=line_id)
    line.delete()
    return redirect('/order/indexline', messages.success(request, 'Line was successfully deleted.', 'alert-success'))

@login_required
def destroyPrice(request, price_id):
    price = Price.objects.get(id=price_id)
    price.delete()
    return redirect('/order/indexprice', messages.success(request, 'Price was successfully deleted.', 'alert-success'))


@login_required
def new_customer_name(request):
    if request.POST:
        customername = CustomerNameForm(request.POST)
        if customername.is_valid():
            if customername.save():
                return redirect('/order/indexcustomername', messages.success(request, 'Customer Name was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexcustomername', messages.error(request, 'Customer Name is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexcustomername', messages.error(request, 'Customer Name is not valid', 'alert-danger'))
    else:
        customer_name_form = CustomerNameForm()
        response = get_value(request.user.id)
        return render(request, 'newcustomername.html', {'customer_name_form':customer_name_form,'response':response})

@login_required 
def index_customer_name(request):
    customername = CustomerName.objects.filter(active='1')
    response = get_value(request.user.id)
    return render(request, 'indexcustomername.html', {'customername': customername,'response':response})

@login_required
def destroy_customer_name(request, customer_id):
   
    if CustomerName.objects.filter(id=customer_id).update(active='0'):
        return redirect('/order/indexcustomername', messages.success(request, 'Customer Name was successfully deleted.', 'alert-success'))  
    else:
        return redirect('/order/indexcustomername', messages.danger(request, 'Cannot delete Customer Name while its order exists.', 'alert-danger'))

@login_required
def new_bill_address(request):
    if request.POST:
        billaddress = BillAddressForm(request.POST)
        if billaddress.is_valid():
            if billaddress.save():
                return redirect('/order/indexbilladdress', messages.success(request, 'Bill address was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexbilladdress', messages.error(request, 'Bill address is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexbilladdress', messages.error(request, 'Bill address is not valid', 'alert-danger'))
    else:
        bill_address_form = BillAddressForm()
        response = get_value(request.user.id)
        return render(request, 'newbilladdress.html', {'bill_address_form':bill_address_form,'response':response})

@login_required
def new_ship_address(request):
    if request.POST:
        shipaddress = ShipAddressForm(request.POST)
        if shipaddress.is_valid():
            if shipaddress.save():
                return redirect('/order/indexshipaddress', messages.success(request, 'Ship address was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexshipaddress', messages.error(request, 'Ship address is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexshipaddress', messages.error(request, 'Ship address is not valid', 'alert-danger'))
    else:
        ship_address_form = ShipAddressForm()
        response = get_value(request.user.id)
        return render(request, 'newshipaddress.html', {'ship_address_form':ship_address_form,'response':response})


@login_required 
def index_bill_address(request):
    billaddress = BillAddress.objects.filter(active='1')
    response = get_value(request.user.id)
    return render(request, 'indexbilladdress.html', {'billaddress': billaddress,'response':response})

def index_ship_address(request):
    shipaddress = ShipAddress.objects.filter(active='1')
    response = get_value(request.user.id)
    return render(request, 'indexshipaddress.html', {'shipaddress':shipaddress,'response':response})

@login_required
def destroy_bill_address(request, billAddress_id):
   
    if BillAddress.objects.filter(id=billAddress_id).update(active='0'):
        return redirect('/order/indexbilladdress', messages.success(request, 'Bill Address was successfully deleted.', 'alert-success'))  
    else:
        return redirect('/order/indexbilladdress', messages.danger(request, 'Cannot delete Bill Address while its order exists.', 'alert-danger'))

@login_required
def destroy_ship_address(request, shipAddress_id):
   
    if ShipAddress.objects.filter(id=shipAddress_id).update(active='0'):
        return redirect('/order/indexshipaddress', messages.success(request, 'Ship Address was successfully deleted.', 'alert-success'))  
    else:
        return redirect('/order/indexshipaddress', messages.danger(request, 'Cannot delete Ship Address while its order exists.', 'alert-danger'))

@login_required
def upload_line(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadline.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    Line.objects.create(
                        order_number = row_values[1] or 0,
                        customer_number = row_values[2] or 0,
                        customer_name = row_values[3] or None,
                        cat = row_values[4] or 0,
                        ship_days = row_values[5] or 0,
                        travel_days = row_values[6] or 0,
                        order_total = row_values[7] or 0,
                        estimated_costs = row_values[8] or 0,
                        line_number = row_values[9] or 0,
                        part_number = row_values[10] or None,
                        description = row_values[11] or None,
                        whse = row_values[12] or 0,
                        alloc = row_values[13] or None,
                        qty_order = row_values[14] or 0,
                        qty_avail = row_values[15] or 0,
                        required_date = datetime(*xlrd.xldate_as_tuple(row_values[16], 0)),
                        promised_date = datetime(*xlrd.xldate_as_tuple(row_values[17], 0)),
                        unit_price = row_values[18] or 0,
                        ship_tolerance_min = row_values[19] or 0,
                        ship_tolerance_max = row_values[20] or 0,
                        uos = row_values[21] or 0,
                        price_book = row_values[22] or 0,
                        stat = row_values[23] or None)
            response = get_value(request.user.id)
            return render(request, 'uploadline.html', {'response':response})
        
@login_required
def upload(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'upload.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    Order.objects.create(
                        purchase_order = row_values[1] or 0,
                        bill_address = row_values[2] or None,
                        ship_address = row_values[3] or None,
                        required_date = datetime(*xlrd.xldate_as_tuple(row_values[4], 0)),
                        freight = row_values[5] or None,
                        quote = row_values[6] or None,
                        contract = row_values[7] or 0,
                        order_status = row_values[8] or None,
                        order_received = row_values[9] or None,
                        price_method = row_values[10] or None,
                        surcharge = row_values[11] or None,
                        A_R_credit = row_values[12] or None,
                        fax_ASN = row_values[13] or None,
                        email_ASN = row_values[14] or None,
                        order_type = row_values[15] or None,
                        order_number = row_values[16] or 0,
                        ordered_date = datetime(*xlrd.xldate_as_tuple(row_values[17], 0)),
                        price_details = row_values[18] or None,
                        kit_details = row_values[19] or None,
                        ship_via = row_values[20] or None,
                        attention = row_values[21] or None,
                        ship_instructions = row_values[22] or None,
                        F_O_B = row_values[23] or None,
                        warehouse = row_values[24] or None,
                        sales_rep = row_values[25] or 0,
                        product_line = row_values[26] or None,
                        COS_project = row_values[27] or 0,
                        sales_account = row_values[28] or 0,
                        order_value = row_values[29] or 0,
                        staus_number = row_values[30] or 0,
                        contact_name = row_values[31] or None,
                        phone_number = row_values[32] or 0,
                        ship_cond = row_values[33] or 0,
                        credit_control = row_values[34] or 0,
                        ASN_contact = row_values[35] or None,
                        ASN_title = row_values[36] or None,
                        ASN_fax_num = row_values[37] or 0,
                        email_addr = row_values[38] or None
                        #billAddress_id_id = row_values[23] or None,
                        #shipAddress_id_id = row_values[23] or None
                        )
            response = get_value(request.user.id)
            return render(request, 'upload.html', {'response':response})
        
@login_required
def upload_bill_address(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadbilladdress.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    BillAddress.objects.create(
                        #id = row_values[0] or 0,
                        bill_address = row_values[1] or None,
                        bill_number = row_values[2] or 0,
                        active = row_values[3] or 0
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadbilladdress.html', {'response':response})
        
@login_required
def upload_ship_address(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadshipaddress.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    ShipAddress.objects.create(
                        #id = row_values[0] or 0,
                        ship_address = row_values[1] or None,
                        ship_number = row_values[2] or 0,
                        active = row_values[3] or 0
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadshipaddress.html', {'response':response})

@login_required
def upload_account(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadaccount.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    Account.objects.create(
                        #id = row_values[0] or 0,
                        account_description = row_values[1] or None,
                        account_number = row_values[2] or 0,
                        active = row_values[3] or 0
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadaccount.html', {'response':response})

@login_required
def upload_part(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadpart.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    Part.objects.create(
                        part_description = row_values[1] or None,
                        part_number = row_values[2] or 0,
                        active = row_values[3] or 0
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadpart.html', {'response':response})

@login_required
def upload_purchase(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadpurchase.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    Purchase.objects.create(
                        requisition_number = row_values[1] or 0,
                        requested_by = row_values[2] or None,
                        entry_date = datetime(*xlrd.xldate_as_tuple(row_values[3], 0)),
                        project_number = row_values[4] or 0,
                        project_description = row_values[5] or None,
                        header_comments = row_values[6] or None,
                        line = row_values[7] or 0,
                        quantity = row_values[8] or 0,
                        required_date = datetime(*xlrd.xldate_as_tuple(row_values[9], 0)),
                        vendor_one = row_values[10] or None,
                        vendor_two = row_values[11] or None,
                        vendor_three = row_values[12] or None,
                        unit_price_one = row_values[13] or 0,
                        unit_price_two = row_values[14] or 0,
                        unit_price_three = row_values[15] or 0,
                        total = row_values[16] or 0,
                        internal_comments = row_values[17] or None,
                        on_hand = row_values[18] or 0,
                        on_order = row_values[19] or 0,
                        reorder_point = row_values[20] or 0,
                        supplier = row_values[21] or None,
                        purchase_quantity = row_values[22] or 0,
                        requisition_status = row_values[23] or None,
                        purchase_type = row_values[24] or None,
                        red_req = row_values[25] or None,
                        ready_for_approval = row_values[26] or None,
                        approved_yn = row_values[27] or None,
                        buyer = row_values[28] or None,
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadpurchase.html', {'response':response})

@login_required
def upload_sales_report(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadsalesreport.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]
        
        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    SalesReport.objects.create(
                        Customerno = row_values[1] or None,
                        Companyname = row_values[2] or None,
                        Die_Number = row_values[3] or None,
                        Invoiceno = row_values[4] or None,
                        Salesorderno = row_values[5] or None,
                        Lineno_Alt = row_values[6] or None,
                        Partno = row_values[7] or None,
                        Partdescr = row_values[8] or None,
                        Dateshipped = datetime(*xlrd.xldate_as_tuple(float(row_values[9]), 0)),
                        Invoicedate = datetime(*xlrd.xldate_as_tuple(float(row_values[10]), 0)),
                        Qty_Shipped = row_values[11] or 0,
                        Calc_Actual_Wgt = row_values[12] or 0,
                        Calc_Theor_Wgt = row_values[13] or 0,
                        Calc_Price = row_values[14] or 0,
                        Extrusion_Revenue = row_values[15] or 0,
                        Price_per_Lb = row_values[16] or 0,
                        Fabrication_Lbs = row_values[17] or 0,
                        Fabrication_Revenue = row_values[18] or 0,
                        Paint_Lbs = row_values[19] or 0,
                        Paint_Revenue = row_values[20] or 0,
                        Anodizing_Sq_Ft = row_values[21] or 0,
                        Anodizing_Revenue = row_values[22] or 0,
                        Ingot_Price = row_values[23] or 0,
                        Press = row_values[24] or None,
                        Ordertype = row_values[25] or None,
                        Unitofmeas = row_values[26] or None,
                        Productline = row_values[27] or None,
                        Shiptono = row_values[28] or None,
                        Ship_To_State = row_values[29] or None,
                        RSM = row_values[30] or None,
                        RSM_name = row_values[31] or None,                        
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadsalesreport.html', {'response':response})

@login_required
def upload_purchase_report(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadpurchasereport.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    PurchaseReport.objects.create(
                        P_O = row_values[1] or None,
                        Vendor_No = row_values[2] or None,
                        Vendor_Name = row_values[3] or None,
                        line = row_values[4] or None,
                        Partno = row_values[5] or None,
                        Partdescr = row_values[6] or None,
                        GL_Accountno = row_values[7] or None,
                        Datepromised = datetime(*xlrd.xldate_as_tuple(row_values[8], 0)),
                        Qtyonorder = row_values[9] or 0,
                        Price = row_values[10] or 0,
                        Line_Amount = row_values[11] or 0,
                        Requestedby = row_values[12] or None,
                        Buyer = row_values[13] or None,
                        Status = row_values[14] or None,
                        Projectno = row_values[15] or None,
                        Project_Desc = row_values[16] or None,                       
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadpurchasereport.html', {'response':response})

@login_required
def newPurchase(request):
    if request.POST:
        purchase = PurchaseForm(request.POST)
        if purchase.is_valid():
            if purchase.save():
                return redirect('/purchase', messages.success(request, 'New Purchase was successfully created.', 'alert-success'))
            else:
                return redirect('/purchase', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            return redirect('/purchase', messages.error(request, 'Purchase is not valid', 'alert-danger'))
    else:
        purchase = PurchaseForm()
        response = get_value(request.user.id)
        return render(request, 'newpurchase.html', {'purchase':purchase,'response':response})
    
@login_required
def indexPurchase(request):
    purchase = Purchase.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexpurchase.html', {'purchase': purchase,'response':response})

@login_required
def destroyPurchase(request, purchase_id):
    purchase = Purchase.objects.get(id=purchase_id)
    purchase.delete()
    return redirect('/purchase', messages.success(request, 'Purchase was successfully deleted.', 'alert-success'))

@login_required
def editPurchase(request, purchase_id):
    purchase = Purchase.objects.get(id=purchase_id)
    if request.POST:
        purchase = PurchaseForm(request.POST, instance=purchase)
        if purchase.is_valid():
            if purchase.save():
                return redirect('/purchase', messages.success(request, 'Purchase was successfully updated.', 'alert-success'))
            else:
                return redirect('/purchase', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            return redirect('/purchase', messages.error(request, 'Purchase is not valid', 'alert-danger'))
    else:
        purchase = PurchaseForm(instance=purchase)
        response = get_value(request.user.id)
        return render(request, 'editpurchase.html', {'purchase':purchase,'response':response})


@login_required
def new_part(request):
    if request.POST:
        part = PartForm(request.POST)
        if part.is_valid():
            if part.save():
                return redirect('/purchase/indexpart', messages.success(request, 'Part was successfully created.', 'alert-success'))
            else:
                return redirect('/purchase/indexpart', messages.error(request, 'Part is not saved', 'alert-danger'))
        else:
            return redirect('/purchase/indexpart', messages.error(request, 'Part is not valid', 'alert-danger'))
    else:
        part = PartForm()
        response = get_value(request.user.id)
        return render(request, 'newpart.html', {'part':part,'response':response})

@login_required
def new_account(request):
    if request.POST:
        account = AccountForm(request.POST)
        if account.is_valid():
            if account.save():
                return redirect('/purchase/indexaccount', messages.success(request, 'Account was successfully created.', 'alert-success'))
            else:
                return redirect('/purchase/indexaccount', messages.error(request, 'Account is not saved', 'alert-danger'))
        else:
            return redirect('/purchase/indexaccount', messages.error(request, 'Account is not valid', 'alert-danger'))
    else:
        account = AccountForm()
        response = get_value(request.user.id)
        return render(request, 'newaccount.html', {'account':account,'response':response})


@login_required 
def index_part(request):
    part = Part.objects.filter(active='1')
    response = get_value(request.user.id)
    return render(request, 'indexpart.html', {'part': part,'response':response})
@login_required 
def index_account(request):
    account = Account.objects.filter(active='1')
    response = get_value(request.user.id)
    return render(request, 'indexaccount.html', {'account':account,'response':response})

@login_required
def destroy_part(request, part_id):
   
    if Part.objects.filter(id=part_id).update(active='0'):
        return redirect('/purchase/indexpart', messages.success(request, 'Part was successfully deleted.', 'alert-success'))  
    else:
        return redirect('/purchase/indexpart', messages.danger(request, 'Cannot delete Part while its order exists.', 'alert-danger'))

@login_required
def destroy_account(request, account_id):
   
    if Account.objects.filter(id=account_id).update(active='0'):
        return redirect('/purchase/indexaccount', messages.success(request, 'Account was successfully deleted.', 'alert-success'))  
    else:
        return redirect('/purchase/indexaccount', messages.danger(request, 'Cannot delete Account while its order exists.', 'alert-danger'))


@login_required
def new_price(request):
    if request.POST:
        price = PriceForm(request.POST)
        if price.is_valid():
            if price.save():
                return redirect('/order/indexprice', messages.success(request, 'Price was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexprice', messages.error(request, 'Price is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexprice', messages.error(request, 'Price is not valid', 'alert-danger'))
    else:
        price = PriceForm()
        response = get_value(request.user.id)
        return render(request, 'price.html', {'price':price,'response':response})
    
@login_required
def new_billet(request):
    if request.POST:
        billet = BilletForm(request.POST)
        if billet.is_valid():
            if billet.save():
                return redirect('/order/indexbillet', messages.success(request, 'Billet data was successfully entered.', 'alert-success'))
            else:
                return redirect('/order/indexbillet', messages.error(request, 'Billet data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexbillet', messages.error(request, 'Billet data is not valid', 'alert-danger'))
    else:
        billet = BilletForm()
        response = get_value(request.user.id)
        return render(request, 'newbillet.html', {'billet':billet,'response':response})

@login_required
def index_billet(request):
    billet = Billet.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexbillet.html', {'billet': billet,'response':response})

@login_required
def editBillet(request, billet_id):
    billet = Billet.objects.get(id=billet_id)
    if request.POST:
        billet = BilletForm(request.POST, instance=billet)
        if billet.is_valid():
            if billet.save():
                return redirect('/order/indexbillet', messages.success(request, 'New Billet data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexbillet', messages.error(request, 'Data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexbillet', messages.error(request, 'Billet Data is not valid', 'alert-danger'))
    else:
        billet = BilletForm(instance=billet)
        response = get_value(request.user.id)
        return render(request, 'editbillet.html', {'billet':billet,'response':response})

@login_required
def showBillet(request, billet_id):
    billet = Billet.objects.filter(id=billet_id)
    response = get_value(request.user.id)
    return render(request, 'showbillet.html', {'billet': billet,'response':response})

@login_required
def destroyBillet(request, billet_id):
    billet = Billet.objects.get(id=billet_id)
    billet.delete()
    return redirect('/order/indexbillet', messages.success(request, 'Billet Data was successfully deleted.', 'alert-success'))

@login_required
def new_log(request):
    if request.POST:
        log = LogForm(request.POST)
        if log.is_valid():
            if log.save():
                return redirect('/order/indexlog', messages.success(request, 'New Log data was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexlog', messages.error(request, 'Log data is not saved', 'alert-danger'))
        else:
            print(log.errors)
            return redirect('/order/indexlog', messages.error(request, 'Log data is not valid', 'alert-danger'))
    else:
        log = LogForm()
        response = get_value(request.user.id)
        return render(request, 'newlog.html', {'log':log,'response':response})

@login_required
def index_log(request):
    log = Log.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexlog.html', {'log': log,'response':response})

@login_required
def editLog(request, log_id):
    log = Log.objects.get(id=log_id)
    if request.POST:
        log = LogForm(request.POST, instance=log)
        if log.is_valid():
            if log.save():
                return redirect('/order/indexlog', messages.success(request, 'New Log data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexlog', messages.error(request, 'Log data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexlog', messages.error(request, 'Log data is not valid', 'alert-danger'))
    else:
        log = LogForm(instance=log)
        response = get_value(request.user.id)
        return render(request, 'editlog.html', {'log':log,'response':response})

@login_required
def showLog(request, log_id):
    log = Log.objects.filter(id=log_id)
    response = get_value(request.user.id)
    return render(request, 'showlog.html', {'log': log,'response':response})
    
@login_required
def destroyLog(request, log_id):
    log = Log.objects.get(id=log_id)
    log.delete()
    return redirect('/order/indexlog', messages.success(request, 'Log Data was successfully deleted.', 'alert-success'))
'''
@login_required
def index_metal(request):
    summary_initial = GeneralReport.objects.filter(Transamnt__gt=0)
    summary_foundry_metal = summary_initial.filter(Accountno=5100717) | summary_initial.filter(Accountno=5100726) |\
                             summary_initial.filter(Accountno=5100716) | summary_initial.filter(Accountno=5100710) |\
                             summary_initial.filter(Accountno=5100715) | summary_initial.filter(Accountno=5100720) |\
                             summary_initial.filter(Accountno=5100719) | summary_initial.filter(Accountno=5100714) |\
                             summary_initial.filter(Accountno=5100711) | summary_initial.filter(Accountno=5100707) |\
                             summary_initial.filter(Accountno=5100712) | summary_initial.filter(Accountno=5100718)
    summary_metal = summary_foundry_metal.annotate(month=TruncMonth('Transdate')).values('month').annotate(total=Round(Sum('Transamnt'))).order_by()
'''    


@login_required
def department_navigation(request):
    response = get_value(request.user.id)
    return render(request, 'departmentnavigation.html', {'response':response})

@login_required
def department_trend_navigation(request):
    response = get_value(request.user.id)
    return render(request, 'departmenttrendnavigation.html', {'response':response})

@login_required
def new_revenue(request):
    if request.POST:
        revenue = RevenueForm(request.POST)
        if revenue.is_valid():
            if revenue.save():
                return redirect('/order/indexrevenue', messages.success(request, 'New Revenue data was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexrevenue', messages.error(request, 'Revenue data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexrevenue', messages.error(request, 'Revenue data is not valid', 'alert-danger'))
    else:
        revenue = RevenueForm()
        response = get_value(request.user.id)
        return render(request, 'newrevenue.html', {'revenue':revenue,'response':response})


@login_required
def index_revenue(request):
    revenue = Revenue.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexrevenue.html', {'revenue': revenue,'response':response})

@login_required
def editRevenue(request, revenue_id):
    revenue = Revenue.objects.get(id=revenue_id)
    if request.POST:
        revenue = RevenueForm(request.POST, instance=revenue)
        if revenue.is_valid():
            if revenue.save():
                return redirect('/order/indexrevenue', messages.success(request, 'New Revenue data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexrevenue', messages.error(request, 'Revenue data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexrevenue', messages.error(request, 'Revenue data is not valid', 'alert-danger'))
    else:
        revenue = RevenueForm(instance=revenue)
        response = get_value(request.user.id)
        return render(request, 'editrevenue.html', {'revenue':revenue,'response':response})

@login_required
def showRevenue(request, revenue_id):
    revenue = Revenue.objects.filter(id=revenue_id)
    response = get_value(request.user.id)
    return render(request, 'showrevenue.html', {'revenue': revenue,'response':response})
    
@login_required
def destroyRevenue(request, revenue_id):
    revenue = Revenue.objects.get(id=revenue_id)
    revenue.delete()
    return redirect('/order/indexrevenue', messages.success(request, 'Revenue Data was successfully deleted.', 'alert-success'))

@login_required
def upload_revenue(request):
    if "GET" == request.method:
        response = get_value(request.user.id)
        return render(request, 'uploadrevenue.html', {'response':response})
    else:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
        if file_type in ['xlsx', 'xls']:   # 支持这两种文件格式
            # 打开工作文件
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
            # 循环获取每个数据表中的数据并写入数据库
            for table in tables:
                rows = table.nrows   # 总行数
                for row in range(1, rows):  # 从1开始是为了去掉表头
                    row_values = table.row_values(row)  # 每一行的数据                    
                    Revenue.objects.create(
                        date = datetime(*xlrd.xldate_as_tuple(row_values[1], 0)),
                        revenue = row_values[2] or 0,                     
                        )
            response = get_value(request.user.id)
            return render(request, 'uploadrevenue.html',{'response':response})

@login_required
def revenue_chart(request):
    summary_initial = Revenue.objects.filter(revenue__gt=0)
    summary_gross_revenue = summary_initial.annotate(month=TruncMonth('date')).values('month').annotate(total=Round(Sum('revenue'))).order_by()
    gross_revenue =  DataPool(
           series=
            [{'options': {
            'source': summary_gross_revenue},
                'terms': [{'month': 'month',
                'gross revenue': 'total'}]
                },

       
             ])
    cht = Chart(
            datasource = gross_revenue,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                  'month': [
                    'gross revenue']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Gross Revenue Amount All Times - Column Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Gross Revenue'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})  

    cht2 = Chart(
            datasource = gross_revenue,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'gross revenue']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Gross Revenue Amount All Times - Line Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Gross Revenue'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})

    cht3 = Chart(
            datasource = gross_revenue,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'month': [
                    'gross revenue']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Gross Revenue Amount All Times - Pie Chart'},
               'xAxis': {
                   'title':{'text': 'Month'}},
               'yAxis': {
                   'title': {'text': 'Gross Revenue'}},
                'legend': {
                    'enabled': True},
                'credits': {
                    'enabled': False}})
    response = get_value(request.user.id)
    return render(request,'revenuechart.html', 
        {'chart_list': [cht, cht2, cht3],'response':response})

@login_required
def check_sales(request, sales_id):
    sales = SalesReport.objects.filter(id=sales_id)
    response = get_value(request.user.id)
    return render(request, 'checksalesreport.html', {'sales':sales,'response':response})

@login_required
def check_purchase(request, purchase_id):
    purchase = PurchaseReport.objects.filter(id=purchase_id)
    response = get_value(request.user.id)
    return render(request, 'checkpurchasereport.html', {'purchase':purchase,'response':response})

@login_required
def check_general(request, general_id):
    general = GeneralReport.objects.filter(id=general_id)
    response = get_value(request.user.id)
    return render(request, 'checkgeneralreport.html', {'general':general,'response':response})
@login_required
def new_foundry(request):
    if request.POST:
        foundry = FoundryForm(request.POST)
        if foundry.is_valid():
            if foundry.save():
                return redirect('/order/indexfoundry', messages.success(request, 'New Foundry data was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexfoundry', messages.error(request, 'Foundry data is not saved', 'alert-danger'))
        else:
            print(log.errors)
            return redirect('/order/indexfoundry', messages.error(request, 'Foundry data is not valid', 'alert-danger'))
    else:
        foundry = FoundryForm()
        response = get_value(request.user.id)
        return render(request, 'newfoundry.html', {'foundry':foundry,'response':response})

@login_required
def index_foundry(request):
    foundry = Foundry.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexfoundry.html', {'foundry': foundry,'response':response})

@login_required
def editFoundry(request, foundry_id):
    foundry = Foundry.objects.get(id=foundry_id)
    if request.POST:
        foundry = FoundryForm(request.POST, instance=foundry)
        if foundry.is_valid():
            if foundry.save():
                return redirect('/order/indexfoundry', messages.success(request, 'New Foundry data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexfoundry', messages.error(request, 'Foundry data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexfoundry', messages.error(request, 'Foundry data is not valid', 'alert-danger'))
    else:
        foundry = FoundryForm(instance=foundry)
        response = get_value(request.user.id)
        return render(request, 'editfoundry.html', {'foundry':foundry,'response':response})

@login_required
def destroyFoundry(request, foundry_id):
    foundry = Foundry.objects.get(id=foundry_id)
    foundry.delete()
    return redirect('/order/indexfoundry', messages.success(request, 'Foundry Data was successfully deleted.', 'alert-success'))

'''
@login_required
def new_extrusion(request):
    if request.POST:
        extrusion = ExtrusionForm(request.POST)
        if extrusion.is_valid():
            if extrusion.save():
                return redirect('/order/indexextrusion', messages.success(request, 'New Extrusion data was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexextrusion', messages.error(request, 'Extrusion data is not saved', 'alert-danger'))
        else:
            print(extrusion.errors)
            return redirect('/order/indexextrusion', messages.error(request, 'Extrusion data is not valid', 'alert-danger'))
    else:
        extrusion = ExtrusionForm()
        response = get_value(request.user.id)
        return render(request, 'newextrusion.html', {'extrusion':extrusion,'response':response})

@login_required
def index_extrusion(request):
    extrusion = Extrusion.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexextrusion.html', {'extrusion': extrusion,'response':response})

@login_required
def editExtrusion(request, extrusion_id):
    extrusion = Extrusion.objects.get(id=extrusion_id)
    if request.POST:
        extrusion = ExtrusionForm(request.POST, instance=extrusion)
        if extrusion.is_valid():
            if extrusion.save():
                return redirect('/order/indexextrusion', messages.success(request, 'New Extrusion data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexextrusion', messages.error(request, 'Extrusion data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexextrusion', messages.error(request, 'Extrusion data is not valid', 'alert-danger'))
    else:
        extrusion = ExtrusionForm(instance=extrusion)
        response = get_value(request.user.id)
        return render(request, 'editextrusion.html', {'extrusion':extrusion,'response':response})

@login_required
def destroyExtrusion(request, extrusion_id):
    extrusion = Extrusion.objects.get(id=extrusion_id)
    extrusion.delete()
    return redirect('/order/indexextrusion', messages.success(request, 'Extrusion Data was successfully deleted.', 'alert-success'))
'''

@login_required
def all_receiving(request):
    receiving = Order.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexreceiving.html', {'receiving':receiving,'response':response})



@login_required
def edit_receiving(request,receiving_id):
    receiving = Order.objects.get(id=receiving_id)
    if request.POST:
        payment_status = request.POST.get('payment_status')
        amount_received = request.POST.get('amount_received')
        receiving.payment_status = payment_status
        receiving.amount_received = amount_received
        receiving.save()
        return redirect('/order/allreceiving', messages.success(request, 'New Receiving data was successfully created.', 'alert-success'))
    else:
        receiving = OrderForm(instance=receiving)
        response = get_value(request.user.id)
        return render(request, 'newreceiving.html', {'receiving':receiving,'response':response,'receiving_id':receiving_id})

@login_required
def index_debt(request):
    debt = Order.objects.values('customer_id__customer_number', 'customer_id__customer_name').annotate(total=Round(Sum('order_value')-Sum('amount_received'))).order_by()
    #for item in Order.objects.values('customer_id'):
    #    print(item.id, item.order_value)
    customer = CustomerName.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexdebt.html', {'debt': debt,'customer': customer,'response':response})
    
@login_required
def all_shipping(request):
    shipping = Order.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexshipping.html', {'shipping':shipping,'response':response})

@login_required
def edit_shipping(request,shipping_id):
    shipping = Order.objects.get(id=shipping_id)
    if request.POST:
        shipping_date = request.POST.get('shipping_date')
        shipping_status = request.POST.get('shipping_status')
        shipping_weights = request.POST.get('shipping_weight')
        shipping_due = request.POST.get('shipping_due')
        shipping.shipping_date = shipping_date
        shipping.shipping_status = shipping_status
        shipping.shipping_weight = shipping_weights
        shipping.shipping_due = shipping_due
        shipping.save()
        return redirect('/order/allshipping', messages.success(request, 'New Shipping data was successfully created.', 'alert-success'))
    else:
        shipping = OrderForm(instance=shipping)
        response = get_value(request.user.id)
        return render(request, 'newshipping.html', {'shipping':shipping,'response':response})

@login_required
def index_maintenance(request):
    maintenance = Maintenance.objects.all()
    response = get_value(request.user.id)
    return render(request,'indexmaintenance.html',{'maintenance':maintenance,'response':response})

@login_required
def maintenance(request):
    if request.POST:
        maintenance = MaintenanceForm(request.POST)
        if maintenance.is_valid():
            if maintenance.save():
                return redirect('/order/indexmaintenance', messages.success(request, 'New Maintenance data was successfully created.', 'alert-success'))
            else:
                return redirect('/order/indexmaintenance', messages.error(request, 'Maintenance data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexmaintenance', messages.error(request, 'Maintenance data is not valid', 'alert-danger'))
    else:
        maintenance = MaintenanceForm()
        response = get_value(request.user.id)
        return render(request, 'newmaintenance.html',{'maintenance':maintenance,'response':response})


@login_required
def edit_maintenance(request, maintenance_id):
    maintenance = Maintenance.objects.get(id=maintenance_id)
    if request.POST:
        maintenance = MaintenanceForm(request.POST, instance=maintenance)
        if maintenance.is_valid():
            if maintenance.save():
                return redirect('/order/indexmaintenance', messages.success(request, 'New Maintenance data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/indexmaintenance', messages.error(request, 'Maintenance data is not saved', 'alert-danger'))
        else:
            return redirect('/order/indexmaintenance', messages.error(request, 'Maintenance data is not valid', 'alert-danger'))
    else:
        maintenance = MaintenanceForm(instance=maintenance)
        response = get_value(request.user.id)
        return render(request, 'editmaintenance.html', {'maintenance':maintenance,'response':response})

@login_required
def show_maintenance(request, maintenance_id):
    maintenance = Maintenance.objects.get(id=maintenance_id)
    response = get_value(request.user.id)
    return render(request, 'showmaintenance.html', {'maintenance': maintenance,'response':response})

@login_required
def delete_maintenance(request, maintenance_id):
    maintenance = Maintenance.objects.get(id=maintenance_id)
    maintenance.delete()
    return redirect('/order/indexmaintenance', messages.success(request, 'Maintenance data was successfully deleted.', 'alert-success'))


@login_required
def all_payment(request):
    purchase = Purchase.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexpayment.html', {'purchase': purchase,'response':response})

@login_required
def edit_payment(request,payment_id):
    payment = Purchase.objects.get(id=payment_id)
    if request.POST:
        payment_status = request.POST.get('payment_status')
        amount_paid = request.POST.get('amount_paid')
        payment.payment_status = payment_status
        payment.amount_paid = amount_paid
        payment.save()
        return redirect('/order/allpayment', messages.success(request, 'New Payment data was successfully created.', 'alert-success'))
    else:
        payment = PurchaseForm(instance=payment)
        response = get_value(request.user.id)
        return render(request, 'newpayment.html', {'payment':payment,'response':response})

@login_required
def all_storage(request):
    purchase = Purchase.objects.all()
    response = get_value(request.user.id)
    return render(request, 'indexstorage.html', {'purchase': purchase,'response':response})

@login_required
def edit_storage(request,storage_id):
    storage = Purchase.objects.get(id=storage_id)
    if request.POST:
        arrival_status = request.POST.get('arrival_status')
        storage.arrival_status = arrival_status
        storage.save()
        return redirect('/order/allstorage', messages.success(request, 'New Payment data was successfully created.', 'alert-success'))
    else:
        storage = PurchaseForm(instance=storage)
        response = get_value(request.user.id)
        return render(request, 'newstorage.html', {'storage':storage,'response':response})

@login_required
def todolistextrusion(request):
    orders = Order.objects.all()
    response = get_value(request.user.id)
    department = response.get('department')
    return render(request, 'todolistextrusion.html', {'orders': orders,'response':response})

@login_required
def todo_pending(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.extrusion_completed = 'Pending'
    todo.save()
    return redirect('/order/todolistextrusion')

@login_required
def todo_completed(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.extrusion_completed = 'Completed'
    todo.save()
    return redirect('/order/todolistextrusion')

@login_required
def allstatus(request):
    orders = Order.objects.all()
    response = get_value(request.user.id)
    department = response.get('department')
    return render(request, 'statuschecklist.html', {'orders': orders,'response':response})

@login_required
def todolistshipping(request):
    orders = Order.objects.all()
    response = get_value(request.user.id)
    department = response.get('department')
    return render(request, 'todolistshipping.html', {'orders': orders,'response':response})

@login_required
def todo_pending_shipping(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.shipping_completed = 'Pending'
    todo.save()
    return redirect('/order/todolistshipping')

@login_required
def todo_completed_shipping(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.shipping_completed = 'Completed'
    todo.save()
    return redirect('/order/todolistshipping')

@login_required
def todolistfabrication(request):
    orders = Order.objects.all()
    response = get_value(request.user.id)
    department = response.get('department')
    return render(request, 'todolistfabrication.html', {'orders': orders,'response':response})

@login_required
def todo_pending_fabrication(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.fabrication_completed = 'Pending'
    todo.save()
    return redirect('/order/todolistfabrication')

@login_required
def todo_completed_fabrication(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.fabrication_completed = 'Completed'
    todo.save()
    return redirect('/order/todolistfabrication')

@login_required
def todolistanodizing(request):
    orders = Order.objects.all()
    response = get_value(request.user.id)
    department = response.get('department')
    return render(request, 'todolistanodizing.html', {'orders': orders,'response':response})

@login_required
def todo_pending_anodizing(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.anodizing_completed = 'Pending'
    todo.save()
    return redirect('/order/todolistanodizing')

@login_required
def todo_completed_anodizing(request, order_id):
    todo = Order.objects.get(id=order_id)
    todo.anodizing_completed = 'Completed'
    todo.save()
    return redirect('/order/todolistanodizing')


def all_injection(request):
    injection = Capitalinjection.objects.all()
    response = get_value(request.user.id)
    return render(request,'indexinjection.html',{'injection':injection,'response':response})

@login_required
def add_injection(request):
    if request.POST:
        injection = CapitalinjectionForm(request.POST)
        if injection.is_valid():
            if injection.save():
                return redirect('/order/all_injection', messages.success(request, 'New Injection data was successfully created.', 'alert-success'))
            else:
                return redirect('/order/all_injection', messages.error(request, 'Injection data is not saved', 'alert-danger'))
        else:
            return redirect('/order/all_injection', messages.error(request, 'Injection data is not valid', 'alert-danger'))
    else:
        injection = CapitalinjectionForm()
        response = get_value(request.user.id)
        return render(request, 'newinjection.html',{'injection':injection,'response':response})

@login_required
def edit_injection(request, injection_id):
    injection = Capitalinjection.objects.get(id=injection_id)
    if request.POST:
        injection = CapitalinjectionForm(request.POST, instance=injection)
        if injection.is_valid():
            if injection.save():
                return redirect('/order/all_injection', messages.success(request, 'New Injection data was successfully updated.', 'alert-success'))
            else:
                return redirect('/order/all_injection', messages.error(request, 'Injection data is not saved', 'alert-danger'))
        else:
            return redirect('/order/all_injection', messages.error(request, 'Injection data is not valid', 'alert-danger'))
    else:
        injection = CapitalinjectionForm(instance = injection)
        response = get_value(request.user.id)
        return render(request, 'editinjection.html', {'injection':injection,'response':response})


@login_required
def show_injection(request, injection_id):
    injection = Capitalinjection.objects.get(id=injection_id)
    response = get_value(request.user.id)
    return render(request, 'showinjection.html', {'injection': injection,'response':response})

@login_required
def delete_injection(request, injection_id):
    injection = Capitalinjection.objects.get(id=injection_id)
    injection.delete()
    return redirect('/order/all_injection', messages.success(request, 'Injection data was successfully deleted.', 'alert-success'))
