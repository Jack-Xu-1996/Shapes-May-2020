from django.contrib import admin
# Register your models here.
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
UserAdmin.fieldsets += (('department', {'fields': ('department',)}),)
UserAdmin.fieldsets += (('position', {'fields': ('position',)}),)
UserAdmin.list_display += ('department',)
UserAdmin.list_display += ('position',)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
