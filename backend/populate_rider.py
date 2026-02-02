import os
import django
import random
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery.settings')
django.setup()

from core.models import User, Shop, Order, OrderItem, Dish, Address

def create_rider_data():
    print("开始配置北京骑手及相关数据...")

    # 1. 创建北京骑手
    rider, created = User.objects.get_or_create(username='rider_beijing', defaults={
        'email': 'rider_bj@example.com',
        'role': 'rider',
        'phone': '13800138000'
    })
    if created:
        rider.set_password('password123')
        rider.save()
        print("  - 创建骑手: rider_beijing (密码: password123)")
    else:
        print("  - 骑手 rider_beijing 已存在")

    # 2. 获取北京的商家 (例如 mcd_beijing_new 或其他北京店铺)
    # 假设我们用 'mcd_beijing_new' 的店铺，或者 'bj_special_food'
    shops = Shop.objects.filter(address__contains='北京')
    if not shops.exists():
        print("  ! 未找到北京商家，请先运行 populate_db_extra.py")
        return

    target_shop = shops.first()
    print(f"  - 目标商家: {target_shop.name}")

    # 3. 创建一些历史完成订单 (虚拟记录)
    customer = User.objects.filter(role='customer').first()
    if not customer:
        customer, _ = User.objects.get_or_create(username='mock_customer', role='customer')
        customer.set_password('123')
        customer.save()
    
    # 获取一些菜品
    dishes = list(Dish.objects.filter(shop=target_shop))
    if not dishes:
        # 如果店铺没菜品，借用其他的或跳过
        dishes = list(Dish.objects.all())[:3]

    address, _ = Address.objects.get_or_create(user=customer, defaults={
        'name': '模拟顾客', 'phone': '13900000000', 'address': '北京市朝阳区模拟小区',
        'latitude': 39.91, 'longitude': 116.41
    })

    print("  - 生成历史订单记录...")
    for i in range(5):
        order = Order.objects.create(
            customer=customer,
            shop=target_shop,
            rider=rider,
            status='delivered',
            payment_method='wechat',
            payment_time=timezone.now(),
            total_price=0,
            address=address
        )
        
        # 添加订单项
        total = 0
        if dishes:
            dish = random.choice(dishes)
            qty = random.randint(1, 3)
            price = dish.price
            OrderItem.objects.create(order=order, dish=dish, quantity=qty, price=price)
            total += price * qty
        
        order.total_price = total
        order.save()
    print(f"    已生成 5 条历史完成订单")

    # 4. 寻找该商家处于 'cooking' 状态的订单，并指派给该骑手 (模拟接单)
    # 如果没有，就创建一个
    cooking_orders = Order.objects.filter(shop=target_shop, status='cooking')
    
    if cooking_orders.exists():
        for order in cooking_orders:
            order.status = 'delivering'
            order.rider = rider
            order.save()
            print(f"  - 订单 #{order.id} 已被 rider_beijing 接单 (状态更新为: 配送中)")
    else:
        # 创建一个正在配送的订单
        print("  - 未找到制作中的订单，自动创建一个配送中订单...")
        active_order = Order.objects.create(
            customer=customer,
            shop=target_shop,
            rider=rider,
            status='delivering', # 直接设为配送中
            payment_method='wechat',
            payment_time=timezone.now(),
            total_price=0,
            address=address
        )
        if dishes:
            dish = random.choice(dishes)
            OrderItem.objects.create(order=active_order, dish=dish, quantity=1, price=dish.price)
            active_order.total_price = dish.price
            active_order.save()
        print(f"    已创建活跃订单 #{active_order.id}")

if __name__ == '__main__':
    create_rider_data()
