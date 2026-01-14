from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, ShopViewSet, DishViewSet, 
    CategoryViewSet, AddressViewSet, OrderViewSet,
    UserViewSet, CouponViewSet, UserCouponViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet)
router.register(r'shops', ShopViewSet)
router.register(r'dishes', DishViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'user_coupons', UserCouponViewSet, basename='user_coupon')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
