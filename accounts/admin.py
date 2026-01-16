from django.contrib import admin
from .models import Account
# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name','last_login','date_joined', 'is_admin')
    list_filter = ('is_admin',)
    list_display_links = ('email', 'username')
    search_fields = ('email', 'username')

admin.site.register(Account, AccountAdmin)

