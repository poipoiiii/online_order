from django.contrib import admin
from django.urls import path, include
from order import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 页面路由
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('customer/', views.customer_home, name='customer_home'),
    path('customer/orders/', views.customer_orders, name='customer_orders'),
    path('customer/merchant/<int:merchant_id>/', views.customer_merchant, name='customer_merchant'),
    path('merchant/', views.merchant_home, name='merchant_home'),
    path('merchant/orders/', views.merchant_orders, name='merchant_orders'),
    
    # API 路由
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/user-info/', views.api_user_info, name='api_user_info'),
    path('api/merchants/', views.api_merchants, name='api_merchants'),
    path('api/merchants/<int:merchant_id>/dishes/', views.api_merchant_dishes, name='api_merchant_dishes'),
    path('api/merchant/dishes/', views.api_merchant_manage_dishes, name='api_merchant_manage_dishes'),
    path('api/merchant/orders/', views.api_merchant_orders, name='api_merchant_orders'),  # 新增
    path('api/orders/', views.api_user_orders, name='api_user_orders'),
    path('api/orders/create/', views.api_create_order, name='api_create_order'),
    path('api/orders/<int:order_id>/status/', views.api_update_order_status, name='api_update_order_status'),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)