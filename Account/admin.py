from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
# Register your models here.


class AccountAdmin(UserAdmin):
    
    ordering = ('email',)
    
    list_display= ('uid','email','username','create_at','is_staff', 'is_active', 'is_admin')
    
    
    search_fields = ('email', 'username')
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
    add_fieldsets = (
        (None, {
            'fields': ('email', 'username','password1', 'password2', 'birth_date' ),
        }),
    )
    
    # exclude = ('email', 'password1', 'password2', 'username','created_at', 'updated_at',)

admin.site.register(Account, AccountAdmin)