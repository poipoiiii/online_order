from rest_framework import serializers
from .models import User, Shop, Category, Dish, Address, Order, OrderItem, Coupon, UserCoupon, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'avatar']
        read_only_fields = ['role']

    def update(self, instance, validated_data):
        # 允许更新 username, phone, avatar
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        if 'avatar' in validated_data:
            instance.avatar = validated_data['avatar']
        instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    lat = serializers.FloatField(write_only=True, required=False)
    lng = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'phone', 'address', 'lat', 'lng']

    def create(self, validated_data):
        # 移除不在 User 模型中的字段
        validated_data.pop('address', None)
        validated_data.pop('lat', None)
        validated_data.pop('lng', None)
        user = User.objects.create_user(**validated_data)
        return user

class ShopSerializer(serializers.ModelSerializer):
    merchant_name = serializers.ReadOnlyField(source='merchant.username')
    
    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = ['merchant', 'rating']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    shop_name = serializers.ReadOnlyField(source='shop.name')
    
    class Meta:
        model = Dish
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.ReadOnlyField(source='dish.name')
    dish_image = serializers.ImageField(source='dish.image', read_only=True)
    dish_image_url = serializers.ReadOnlyField(source='dish.image_url')

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shop_name = serializers.ReadOnlyField(source='shop.name')
    shop_address = serializers.ReadOnlyField(source='shop.address')
    customer_name = serializers.ReadOnlyField(source='customer.username')
    rider_name = serializers.ReadOnlyField(source='rider.username')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    address_info = AddressSerializer(source='address', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['customer', 'total_price', 'created_at', 'updated_at']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    coupon_id = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.all(), source='coupon', write_only=True
    )
    
    class Meta:
        model = UserCoupon
        fields = '__all__'
        read_only_fields = ['user']

class ReviewSerializer(serializers.ModelSerializer):
    shop_name = serializers.ReadOnlyField(source='shop.name')
    user_name = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
