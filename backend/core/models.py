from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import get_lat_lng

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', '顾客'),
        ('merchant', '商家'),
        ('rider', '骑手'),
        ('admin', '管理员'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer', verbose_name='角色')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='电话')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class Shop(models.Model):
    merchant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop', verbose_name='商家')
    name = models.CharField(max_length=100, verbose_name='店铺名称')
    address = models.CharField(max_length=200, verbose_name='店铺地址')
    # 新增经纬度
    latitude = models.FloatField(default=0.0, verbose_name='纬度')
    longitude = models.FloatField(default=0.0, verbose_name='经度')
    
    description = models.TextField(blank=True, verbose_name='店铺描述')
    image = models.ImageField(upload_to='shops/', blank=True, null=True, verbose_name='店铺图片')
    # 如果没有上传图片，可以存储一个外部URL
    image_url = models.URLField(blank=True, null=True, verbose_name='图片URL')
    
    is_open = models.BooleanField(default=True, verbose_name='营业状态')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name='评分')

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name

class Category(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='categories', verbose_name='所属店铺')
    name = models.CharField(max_length=50, verbose_name='分类名称')
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '菜品分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.shop.name} - {self.name}"

class Dish(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='dishes', verbose_name='所属店铺')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='dishes', verbose_name='分类')
    name = models.CharField(max_length=100, verbose_name='菜品名称')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    description = models.TextField(blank=True, verbose_name='描述')
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name='图片')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片URL')
    
    stock = models.IntegerField(default=999, verbose_name='库存')
    is_available = models.BooleanField(default=True, verbose_name='是否上架')
    
    TAG_CHOICES = (
        ('flash_sale', '限时秒杀'),
        ('daily_deal', '每日优惠'),
        ('big_brand', '大牌一口价'),
    )
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, blank=True, null=True, verbose_name='活动标签')

    class Meta:
        verbose_name = '菜品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    name = models.CharField(max_length=50, verbose_name='联系人')
    phone = models.CharField(max_length=15, verbose_name='电话')
    address = models.CharField(max_length=200, verbose_name='详细地址')
    # 新增经纬度
    latitude = models.FloatField(default=0.0, verbose_name='纬度')
    longitude = models.FloatField(default=0.0, verbose_name='经度')
    
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if self.address and (self.latitude == 0.0 or self.longitude == 0.0):
            self.latitude, self.longitude = get_lat_lng(self.address)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.address}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('unpaid', '待支付'),
        ('pending', '待接单'),
        ('accepted', '已接单'),
        ('cooking', '制作中'),
        ('delivering', '配送中'),
        ('delivered', '已送达'),
        ('cancelled', '已取消'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders', verbose_name='顾客')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_orders', verbose_name='店铺')
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rider_orders', verbose_name='骑手')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True, verbose_name='支付方式')
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name='支付时间')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, verbose_name='收货地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='菜品')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')

    class Meta:
        verbose_name = '订单详情'
        verbose_name_plural = verbose_name

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='优惠码')
    discount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='折扣金额')
    valid_from = models.DateTimeField(verbose_name='生效时间')
    valid_to = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        verbose_name = '优惠券'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.code} - ￥{self.discount}"

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons', verbose_name='用户')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name='优惠券')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    
    class Meta:
        verbose_name = '用户优惠券'
        verbose_name_plural = verbose_name

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review', verbose_name='订单')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews', verbose_name='店铺')
    rating = models.IntegerField(default=5, verbose_name='评分')
    comment = models.TextField(blank=True, verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')

    class Meta:
        verbose_name = '评价'
        verbose_name_plural = verbose_name
