"""DOMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from orders import views as my_order
from django.contrib.auth import views as auth
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^order/uploadline/$',my_order.upload_line,name='uploadline'),
    url(r'^order/upload/$',my_order.upload,name='upload'),
    url(r'^order/uploadbilladdress/$',my_order.upload_bill_address,name='uploadbilladdress'),
    url(r'^order/uploadshipaddress/$',my_order.upload_ship_address,name='uploadshipaddress'),
    url(r'^purchase/uploadaccount/$',my_order.upload_account,name='uploadaccount'),
    url(r'^purchase/uploadpart/$',my_order.upload_part,name='uploadpart'),
    url(r'^purchase/uploadpurchase/$',my_order.upload_purchase,name='uploadpurchase'),
    url(r'^order/uploadsalesreport/$',my_order.upload_sales_report,name='uploadsalesreport'),
    url(r'^order/uploadpurchasereport/$',my_order.upload_purchase_report,name='uploadpurchasereport'),
    url(r'^order/uploadrevenue/$',my_order.upload_revenue,name='uploadrevenue'),

    url(r'^order/salesbootstrap/$',my_order.BootstrapFilterView, name='bootstrap'),
    url(r'^order/sales3bootstrap/$',my_order.BootstrapFilterView_sales3, name='sales3bootstrap'),
    url(r'^order/purchase2bootstrap/$',my_order.BootstrapFilterView_purchase2, name='purchase2bootstrap'),
    url(r'^order/purchase3bootstrap/$',my_order.BootstrapFilterView_purchase3, name='purchase3bootstrap'),
    url(r'^order/foundry1bootstrap/$',my_order.BootstrapFilterView_foundry1, name='foundry1bootstrap'),
    url(r'^order/foundry2bootstrap/$',my_order.BootstrapFilterView_foundry2, name='foundry2bootstrap'),
    url(r'^order/foundry3bootstrap/$',my_order.BootstrapFilterView_foundry3, name='foundry3bootstrap'),
    url(r'^order/extrusion2bootstrap/$',my_order.BootstrapFilterView_extrusion2, name='extrusion2bootstrap'),
    url(r'^order/extrusion3bootstrap/$',my_order.BootstrapFilterView_extrusion3, name='extrusion3bootstrap'),
    url(r'^order/fabrication2bootstrap/$',my_order.BootstrapFilterView_fabrication2, name='fabrication2bootstrap'),
    url(r'^order/fabrication3bootstrap/$',my_order.BootstrapFilterView_fabrication3, name='fabrication3bootstrap'),
    url(r'^order/anodizing2bootstrap/$',my_order.BootstrapFilterView_anodizing2, name='anodizing2bootstrap'),
    url(r'^order/anodizing3bootstrap/$',my_order.BootstrapFilterView_anodizing3, name='anodizing3bootstrap'),
    url(r'^order/shipping2bootstrap/$',my_order.BootstrapFilterView_shipping2, name='shipping2bootstrap'),
    url(r'^order/shipping3bootstrap/$',my_order.BootstrapFilterView_shipping3, name='shipping3bootstrap'),

    url(r'^order/saleschart/$', my_order.sales_chart, name='saleschart'),
    url(r'^order/indexsalesreport/$', my_order.index_sales_report, name='indexsalesreport'),
    url(r'^order/deletesalesreport/$', my_order.destroy_sales_report, name='destroysalesreport'),

    url(r'^order/purchasechart/$', my_order.purchase_chart, name='purchasechart'),
    url(r'^order/indexpurchasereport/$', my_order.index_purchase_report, name='indexpurchasereport'),
    url(r'^order/deletepurchasereport/$', my_order.destroy_purchase_report, name='destroypurchasereport'),
    
    url(r'^admin/', admin.site.urls),
    url(r'^$', my_order.index_chart, name='index'),
    url(r'^orders$', my_order.index, name='home'),
    url(r'^order/(?P<order_id>\d+)/$', my_order.show, name='show'),

    url(r'^order/price/(?P<price_id>\d+)/$', my_order.showPrice, name='showprice'),
    url(r'^order/new/price/$', my_order.new_price, name='newprice'),
    url(r'^order/indexprice/$', my_order.indexprice, name='indexprice'),
    url(r'^order/editprice/(?P<price_id>\d+)/$', my_order.editPrice, name='editprice'),
    url(r'^order/deleteprice/(?P<price_id>\d+)/$', my_order.destroyPrice, name='deleteprice'),
    
    url(r'^order/line/(?P<line_id>\d+)/$', my_order.showLine, name='showline'),
    url(r'^order/indexline/$', my_order.indexline, name='indexline'),
    url(r'^order/newline/$', my_order.newLine, name='newline'),
    url(r'^order/editline/(?P<line_id>\d+)/$', my_order.editLine, name='editline'),
    url(r'^order/deleteline/(?P<line_id>\d+)/$', my_order.destroyLine, name='deleteline'),


    url(r'^order/newcustomername/$', my_order.new_customer_name, name='newcustomername'),
    url(r'^order/indexcustomername/$', my_order.index_customer_name, name='indexcustomername'),
    url(r'^order/indexcustomername/delete/(?P<customer_id>\d+)/$', my_order.destroy_customer_name, name='destroy_customer_name'),

    url(r'^order/newbilladdress/$', my_order.new_bill_address, name='newbilladdress'),
    url(r'^order/newshipaddress/$', my_order.new_ship_address, name='newshipaddress'),
    url(r'^order/indexbilladdress/$', my_order.index_bill_address, name='indexbilladdress'),
    url(r'^order/indexshipaddress/$', my_order.index_ship_address, name='indexshipaddress'),
    url(r'^order/indexbilladdress/delete/(?P<billAddress_id>\d+)/$', my_order.destroy_bill_address, name='destroy_bill_address'),
    url(r'^order/indexshipaddress/delete/(?P<shipAddress_id>\d+)/$', my_order.destroy_ship_address, name='destroy_ship_address'),

    url(r'^purchase/newpart/$', my_order.new_part, name='newpart'),
    url(r'^purchase/newaccount/$', my_order.new_account, name='newaccount'),
    url(r'^purchase/indexpart/$', my_order.index_part, name='indexpart'),
    url(r'^purchase/indexaccount/$', my_order.index_account, name='indexaccount'),
    url(r'^purchase/indexpart/delete/(?P<part_id>\d+)/$', my_order.destroy_part, name='destroy_part'),
    url(r'^purchase/indexaccount/delete/(?P<account_id>\d+)/$', my_order.destroy_account, name='destroy_account'),

    url(r'^purchase/new/$', my_order.newPurchase, name='newpurchase'),
    url(r'^purchase$', my_order.indexPurchase, name='indexpurchase'),
    url(r'^purchase/edit/(?P<purchase_id>\d+)/$', my_order.editPurchase, name='editpurchase'),
    url(r'^purchase/delete/(?P<purchase_id>\d+)/$', my_order.destroyPurchase, name='deletepurchase'),
    url(r'^purchase/(?P<purchase_id>\d+)/$', my_order.showPurchase, name='showpurchase'),
    
    url(r'^order/new/$', my_order.new, name='new'),
    url(r'^order/edit/(?P<order_id>\d+)/$', my_order.edit, name='edit'),
    url(r'^order/delete/(?P<order_id>\d+)/$', my_order.destroy, name='delete'),
    url(r'^users/login/$', auth.login, {'template_name': 'login.html'}, name='login'),
    url(r'^users/logout/$', auth.logout, {'next_page': '/'}, name='logout'),
    url(r'^users/change_password/$', login_required(auth.password_change), {'post_change_redirect' : '/','template_name': 'change_password.html'}, name='change_password'),

    url(r'^order/billet/(?P<billet_id>\d+)/$', my_order.showBillet, name='showbillet'),
    url(r'^order/newbillet/$', my_order.new_billet, name='newbillet'),
    url(r'^order/indexbillet/$', my_order.index_billet, name='indexbillet'),
    url(r'^order/editbillet/(?P<billet_id>\d+)/$', my_order.editBillet, name='editbillet'),
    url(r'^order/deletebillet/(?P<billet_id>\d+)/$', my_order.destroyBillet, name='deletebillet'),
    
    url(r'^order/log/(?P<log_id>\d+)/$', my_order.showLog, name='showlog'),
    url(r'^order/newlog/$', my_order.new_log, name='newlog'),
    url(r'^order/indexlog/$', my_order.index_log, name='indexlog'),
    url(r'^order/editlog/(?P<log_id>\d+)/$', my_order.editLog, name='editlog'),
    url(r'^order/deletelog/(?P<log_id>\d+)/$', my_order.destroyLog, name='deletelog'),

    url(r'^order/departmentnavigation/$', my_order.department_navigation, name='departmentnavigation'),
    url(r'^order/departmenttrendnavigation/$', my_order.department_trend_navigation, name='departmenttrendnavigation'),

    url(r'^order/foundrychart/$', my_order.foundry_chart, name='foundrychart'),
    url(r'^order/extrusionchart/$', my_order.extrusion_chart, name='extrusionchart'),
    url(r'^order/fabricationchart/$', my_order.fabrication_chart, name='fabricationchart'),
    url(r'^order/anodizingchart/$', my_order.anodizing_chart, name='anodizingchart'),
    url(r'^order/shippingchart/$', my_order.shipping_chart, name='shippingchart'),
    url(r'^order/paintchart/$', my_order.paint_chart, name='paintchart'),

    url(r'^order/revenuechart/$', my_order.revenue_chart, name='revenuechart'),
    url(r'^order/revenue/(?P<revenue_id>\d+)/$', my_order.showRevenue, name='showrevenue'),
    url(r'^order/newrevenue/$', my_order.new_revenue, name='newrevenue'),
    url(r'^order/indexrevenue/$', my_order.index_revenue, name='indexrevenue'),
    url(r'^order/editrevenue/(?P<revenue_id>\d+)/$', my_order.editRevenue, name='editrevenue'),
    url(r'^order/deleterevenue/(?P<revenue_id>\d+)/$', my_order.destroyRevenue, name='deleterevenue'),

    url(r'^order/checksales/(?P<sales_id>\d+)/$', my_order.check_sales, name='checksales'),
    url(r'^order/checkpurchase/(?P<purchase_id>\d+)/$', my_order.check_purchase, name='checkpurchase'),
    url(r'^order/checkgeneral/(?P<general_id>\d+)/$', my_order.check_general, name='checkgeneral'),

    url(r'^order/newfoundry/$', my_order.new_foundry, name='newfoundry'),
    url(r'^order/indexfoundry/$', my_order.index_foundry, name='indexfoundry'),
    url(r'^order/editfoundry/(?P<foundry_id>\d+)/$', my_order.editFoundry, name='editfoundry'),
    url(r'^order/deletefoundry/(?P<foundry_id>\d+)/$', my_order.destroyFoundry, name='deletefoundry'),

    #url(r'^order/newextrusion/$', my_order.new_extrusion, name='newextrusion'),
    #url(r'^order/indexextrusion/$', my_order.index_extrusion, name='indexextrusion'),
    #url(r'^order/editextrusion/(?P<extrusion_id>\d+)/$', my_order.editExtrusion, name='editextrusion'),
    #url(r'^order/deleteextrusion/(?P<extrusion_id>\d+)/$', my_order.destroyExtrusion, name='deleteextrusion'),
    url(r'^order/todolistextrusion/$', my_order.todolistextrusion, name='todolistextrusion'),
    url(r'^order/todo_completed/(?P<order_id>\d+)/$', my_order.todo_completed, name='todo_completed'),
    url(r'^order/todo_pending/(?P<order_id>\d+)/$', my_order.todo_pending, name='todo_pending'),

    url(r'^order/allreceiving/$', my_order.all_receiving, name='allreceiving'),
    url(r'^order/editreceiving/(?P<receiving_id>\d+)$', my_order.edit_receiving, name='editreceiving'),

    url(r'^order/indexdebt/$', my_order.index_debt, name='indexdebt'),

    url(r'^order/allshipping/$', my_order.all_shipping, name='allshipping'),
    url(r'^order/editshipping/(?P<shipping_id>\d+)$', my_order.edit_shipping, name='editshipping'),
    url(r'^order/todolistshipping/$', my_order.todolistshipping, name='todolistshipping'),
    url(r'^order/todo_completed_shipping/(?P<order_id>\d+)/$', my_order.todo_completed_shipping, name='todo_completed_shipping'),
    url(r'^order/todo_pending_shipping/(?P<order_id>\d+)/$', my_order.todo_pending_shipping, name='todo_pending_shipping'),

    url(r'^order/todolistfabrication/$', my_order.todolistfabrication, name='todolistfabrication'),
    url(r'^order/todo_completed_fabrication/(?P<order_id>\d+)/$', my_order.todo_completed_fabrication, name='todo_completed_fabrication'),
    url(r'^order/todo_pending_fabrication/(?P<order_id>\d+)/$', my_order.todo_pending_fabrication, name='todo_pending_fabrication'),

    url(r'^order/todolistanodizing/$', my_order.todolistanodizing, name='todolistanodizing'),
    url(r'^order/todo_completed_anodizing/(?P<order_id>\d+)/$', my_order.todo_completed_anodizing, name='todo_completed_anodizing'),
    url(r'^order/todo_pending_anodizing/(?P<order_id>\d+)/$', my_order.todo_pending_anodizing, name='todo_pending_anodizing'),


    url(r'^order/performance/$', my_order.performance, name='performance'),
    url(r'order/maintenance/$', my_order.maintenance, name='maintenance'),
    url(r'order/indexmaintenance/$', my_order.index_maintenance, name='allmaintenance'),
    url(r'order/editmaintenance/(?P<maintenance_id>\d+)$', my_order.edit_maintenance, name='editmaintenance'),
    url(r'order/deletemaintenance/(?P<maintenance_id>\d+)$', my_order.delete_maintenance, name='deletemaintenance'),
    url(r'order/allpayment/$', my_order.all_payment, name='allpayment'),
    url(r'^order/editpayment/(?P<payment_id>\d+)$', my_order.edit_payment, name='editpayment'),
    url(r'order/allstorage/$', my_order.all_storage, name='allstorage'),
    url(r'^order/editstorage/(?P<storage_id>\d+)$', my_order.edit_storage, name='editstorage'),
    url(r'^order/show_maintenance/(?P<maintenance_id>\d+)/$', my_order.show_maintenance, name='showmaintenance'),

    url(r'^order/statuschecklist/$', my_order.allstatus, name='statuschecklist'),
    url(r'^order/addinjection/$', my_order.add_injection, name='addinjection'),
    url(r'^order/all_injection/$', my_order.all_injection, name='allinjection'),
    url(r'order/editinjection/(?P<injection_id>\d+)$', my_order.edit_injection, name='editinjection'),
    url(r'^order/showinjection/(?P<injection_id>\d+)/$', my_order.show_injection, name='showinjection'),
    url(r'^order/deleteinjection/(?P<injection_id>\d+)/$', my_order.delete_injection, name='deleteinjection'),

]
