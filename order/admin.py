from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user_profile', 'phone', 'is_active']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'merchant', 'price', 'is_available']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'merchant', 'total_amount', 'status', 'created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity', 'price']