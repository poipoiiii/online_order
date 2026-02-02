import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery.settings')
django.setup()

from core.models import User, Shop

def create_extra_data():
    # 批量创建北京特色店铺
    beijing_shops = [
        {
            'name': '北京特色美食店',
            'rating': 4.6,
            'desc': '位于北京的正宗本地口味，欢迎品尝！',
            'lat': 39.9042, 'lng': 116.4074,
            'is_open': True,
            'user': 'bj_special_food'
        },
        {
            'name': '北京第7号美味店',
            'rating': 4.5,
            'desc': '位于北京的优选餐厅，距离市中心约 4 km',
            'lat': 39.9400, 'lng': 116.4070,
            'is_open': True,
            'user': 'bj_shop_7'
        },
        {
            'name': '北京第3号美味店',
            'rating': 4.5,
            'desc': '位于北京的优选餐厅，距离市中心约 1 km',
            'lat': 39.9130, 'lng': 116.4070,
            'is_open': False, # 休息中
            'user': 'bj_shop_3'
        },
        {
            'name': '北京第5号美味店',
            'rating': 3.5,
            'desc': '位于北京的优选餐厅，距离市中心约 3 km',
            'lat': 39.9040, 'lng': 116.4420,
            'is_open': True,
            'user': 'bj_shop_5'
        },
        {
            'name': '北京第6号美味店',
            'rating': 4.7,
            'desc': '位于北京的优选餐厅，距离市中心约 5 km',
            'lat': 39.8590, 'lng': 116.4070,
            'is_open': True,
            'user': 'bj_shop_6'
        },
        {
            'name': '北京第1号美味店',
            'rating': 3.5,
            'desc': '位于北京的优选餐厅，距离市中心约 1 km',
            'lat': 39.8950, 'lng': 116.4070,
            'is_open': True,
            'user': 'bj_shop_1'
        },
        {
            'name': '北京第8号美味店',
            'rating': 4.2,
            'desc': '位于北京的优选餐厅，距离市中心约 3 km',
            'lat': 39.9040, 'lng': 116.3720,
            'is_open': False, # 休息中
            'user': 'bj_shop_8'
        },
        {
            'name': '北京第2号美味店',
            'rating': 4.8,
            'desc': '位于北京的优选餐厅，距离市中心约 5 km',
            'lat': 39.9490, 'lng': 116.4270,
            'is_open': False, # 休息中
            'user': 'bj_shop_2'
        },
        {
            'name': '北京第4号美味店',
            'rating': 4.6,
            'desc': '位于北京的优选餐厅，距离市中心约 4 km',
            'lat': 39.8840, 'lng': 116.4470,
            'is_open': True,
            'user': 'bj_shop_4'
        }
    ]

    print("正在添加北京特色店铺...")
    for shop_data in beijing_shops:
        user, created = User.objects.get_or_create(username=shop_data['user'], defaults={
            'email': f"{shop_data['user']}@example.com",
            'role': 'merchant'
        })
        if created:
            user.set_password('password123')
            user.save()
            
            Shop.objects.get_or_create(merchant=user, defaults={
                'name': shop_data['name'],
                'description': shop_data['desc'],
                'address': f"北京市中心附近模拟地址 {shop_data['name']}",
                'latitude': shop_data['lat'],
                'longitude': shop_data['lng'],
                'rating': shop_data['rating'],
                'is_open': shop_data['is_open'],
                'image_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&auto=format&fit=crop'
            })
            print(f"  - 商家: {shop_data['user']} ({shop_data['name']})")
        else:
            # 如果商家已存在，更新店铺信息
            shop, created = Shop.objects.get_or_create(merchant=user)
            shop.name = shop_data['name']
            shop.description = shop_data['desc']
            shop.latitude = shop_data['lat']
            shop.longitude = shop_data['lng']
            shop.rating = shop_data['rating']
            shop.is_open = shop_data['is_open']
            shop.save()
            print(f"  - 更新商家: {shop_data['user']} ({shop_data['name']})")

if __name__ == '__main__':
    create_extra_data()
