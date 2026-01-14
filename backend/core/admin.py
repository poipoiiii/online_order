from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Shop, Category, Dish, Order, OrderItem, Address

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone', 'avatar')}),
    )

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant', 'address', 'rating', 'is_open')
    list_filter = ('is_open',)
    search_fields = ('name', 'address', 'merchant__username')

class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'category', 'price', 'stock', 'is_available')
    list_filter = ('shop', 'is_available', 'category')
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'shop', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'customer__username', 'shop__name')
    inlines = [OrderItemInline]

admin.site.register(User, CustomUserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Category)
admin.site.register(Dish, DishAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address)
