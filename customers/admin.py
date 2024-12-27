from django.contrib import admin
from .models import Customer, Payment, User, JWTToken
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'total_amount')
    search_fields = ('name', 'phone_number')
    list_filter = ('total_amount',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'description', 'amount', 'date')
    search_fields = ('customer__name', 'description')
    list_filter = ('date',)
    
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
    
    # Define the form to use for creating and updating users
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'groups', 'user_permissions')}
        ),
    )
    

@admin.register(JWTToken)
class JWTTokenAdmin(admin.ModelAdmin):
    """
    Admin panel for managing JWT Tokens.
    """
    list_display = ('user', 'token', 'expires_at', 'created_at', 'updated_at', 'is_valid_status')
    search_fields = ('user__email', 'token')
    list_filter = ('expires_at', 'created_at')
    ordering = ('-created_at',)

    def is_valid_status(self, obj):
        """
        Display whether the token is valid in the admin panel.
        """
        return obj.is_valid()
    is_valid_status.short_description = 'Is Valid'
    is_valid_status.boolean = True