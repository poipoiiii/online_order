from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Shop, Category, Dish, Address, Order, OrderItem
from .serializers import (
    UserSerializer, RegisterSerializer, ShopSerializer, 
    CategorySerializer, DishSerializer, AddressSerializer, 
    OrderSerializer, OrderItemSerializer, CouponSerializer,
    UserCouponSerializer, ReviewSerializer
)
import math

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(methods=['post'], detail=False)
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            if user.role == 'merchant':
                address = request.data.get('address', '待完善')
                lat = request.data.get('lat')
                lng = request.data.get('lng')
                Shop.objects.create(
                    merchant=user, 
                    name=f"{user.username}的店铺", 
                    address=address,
                    latitude=lat,
                    longitude=lng
                )
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Shop.objects.all()
        
        # 距离排序逻辑
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                
                # 简单计算距离并排序（非精确地理计算，仅供演示）
                # 在内存中排序，数据量大时应使用 PostGIS
                shops = []
                for shop in queryset:
                    # 确保 shop 有经纬度
                    if shop.latitude is None or shop.longitude is None:
                        continue
                        
                    # 简单的欧几里得距离近似（不考虑地球曲率），用于粗略排序
                    # 或者使用 Haversine 公式
                    d_lat = lat - shop.latitude
                    d_lng = lng - shop.longitude
                    # 粗略转换：1度纬度约111km，1度经度约111*cos(lat)km
                    # 这里简化计算，假设都在中纬度，1度约等于100km
                    distance_km = math.sqrt(d_lat**2 + d_lng**2) * 100
                    shop.distance = distance_km
                    
                    # 过滤超过5公里的商家
                    if distance_km <= 5:
                        shops.append(shop)
                
                shops.sort(key=lambda x: x.distance)
                return shops
            except ValueError:
                pass
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user)

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['shop', 'category', 'tag']
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = Dish.objects.all()
        user = self.request.user
        
        # 如果是商家查看自己的菜品管理，只返回自己店铺的
        # 这里简单判断：如果未提供 shop 参数且用户是商家，默认看自己的
        if user.is_authenticated and user.role == 'merchant' and not self.request.query_params.get('shop'):
             if hasattr(user, 'shop'):
                 queryset = queryset.filter(shop=user.shop)
        
        shop_id = self.request.query_params.get('shop')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        return queryset

    def perform_create(self, serializer):
        # 自动关联商家的店铺
        if hasattr(self.request.user, 'shop'):
            serializer.save(shop=self.request.user.shop)
        else:
            # 如果不是商家，或者商家没有店铺，抛出错误或允许手动指定(这里假设只有商家能创建)
            serializer.save()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 只能查看自己
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Order.objects.filter(customer=user)
        elif user.role == 'merchant':
            return Order.objects.filter(shop__merchant=user)
        elif user.role == 'rider':
            return Order.objects.filter(status__in=['cooking', 'delivering', 'accepted'])
        elif user.is_staff:
            return Order.objects.all()
        return Order.objects.none()

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        data = request.data
        try:
            shop = Shop.objects.get(id=data['shop_id'])
            address = Address.objects.get(id=data['address_id'])
            items_data = data.get('items', [])
            
            total_price = 0
            order = Order.objects.create(
                customer=request.user,
                shop=shop,
                address=address,
                total_price=0
            )
            
            for item in items_data:
                dish = Dish.objects.get(id=item['dish_id'])
                quantity = item['quantity']
                price = dish.price
                OrderItem.objects.create(
                    order=order,
                    dish=dish,
                    quantity=quantity,
                    price=price
                )
                total_price += price * quantity
                
            order.total_price = total_price
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        payment_method = request.data.get('payment_method')
        
        if order.status != 'unpaid':
             return Response({'error': 'Order is not in unpaid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'pending'  # Paid, now pending merchant acceptance
        order.payment_method = payment_method
        order.payment_time = timezone.now()
        order.save()
        
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            order.status = new_status
            if new_status == 'delivering' and request.user.role == 'rider':
                order.rider = request.user
            order.save()
        return Response(OrderSerializer(order).data)

class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 简化：返回所有有效期内的优惠券，或者用户已领取的
        # 这里演示返回所有可领取的
        now = timezone.now()
        return Coupon.objects.filter(valid_to__gte=now)

class UserCouponViewSet(viewsets.ModelViewSet):
    serializer_class = UserCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        shop_id = self.request.query_params.get('shop')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
