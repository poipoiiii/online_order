import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery.settings')
django.setup()

from core.models import User, Shop, Category, Dish

# 图片资源配置
FOOD_IMAGES = {
    '汉堡': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop',
    '披萨': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&auto=format&fit=crop',
    '面条': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop',
    '炸鸡': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500&auto=format&fit=crop',
    '米饭': 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop',
    '寿司': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=500&auto=format&fit=crop',
    '沙拉': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop',
    '咖啡': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=500&auto=format&fit=crop',
    '蛋糕': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&auto=format&fit=crop',
    '烤肉': 'https://images.unsplash.com/photo-1544025162-d76690b67f11?w=500&auto=format&fit=crop'
}

# 城市坐标配置 (中心点)
CITIES = [
    {'name': 'beijing', 'alias': '北京', 'lat': 39.9042, 'lng': 116.4074},
    {'name': 'shanghai', 'alias': '上海', 'lat': 31.2304, 'lng': 121.4737},
    {'name': 'guangzhou', 'alias': '广州', 'lat': 23.1291, 'lng': 113.2644},
    {'name': 'shenzhen', 'alias': '深圳', 'lat': 22.5431, 'lng': 114.0579},
    {'name': 'chengdu', 'alias': '成都', 'lat': 30.5728, 'lng': 104.0668},
    {'name': 'hangzhou', 'alias': '杭州', 'lat': 30.2741, 'lng': 120.1551}
]

def get_image_for_dish(name):
    for key, url in FOOD_IMAGES.items():
        if key in name:
            return url
    return random.choice(list(FOOD_IMAGES.values()))

def create_initial_data():
    print("开始生成分布在城市各处的演示数据...")
    
    # 清空旧数据 (可选)
    # Shop.objects.all().delete()
    # User.objects.filter(role='merchant').delete()
    
    for city in CITIES:
        print(f"正在生成 {city['alias']} 的商家...")
        
        # 在每个城市生成 5-8 个商家，分布在中心点 5km 范围内
        # 1度纬度 ~= 111km，5km ~= 0.045度
        
        for i in range(random.randint(5, 8)):
            # 随机生成偏移量 (-0.04 到 0.04)
            lat_offset = random.uniform(-0.04, 0.04)
            lng_offset = random.uniform(-0.04, 0.04)
            
            shop_lat = city['lat'] + lat_offset
            shop_lng = city['lng'] + lng_offset
            
            username = f"merchant_{city['name']}_{i}"
            shop_name = f"{city['alias']}第{i+1}号美味店"
            
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': f"{username}@example.com",
                'role': 'merchant'
            })
            if created:
                user.set_password('password123')
                user.save()
            
            shop, created = Shop.objects.get_or_create(merchant=user, defaults={
                'name': shop_name,
                'description': f"位于{city['alias']}的优选餐厅，距离市中心约 {random.randint(1,5)} km",
                'address': f"{city['alias']}模拟地址{i}号",
                'latitude': shop_lat,
                'longitude': shop_lng,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'image_url': 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=500&auto=format&fit=crop',
                'is_open': random.choice([True, True, True, False]) # 大部分开门
            })
            
            # 更新坐标
            shop.latitude = shop_lat
            shop.longitude = shop_lng
            shop.save()
            
            # 创建菜品
            categories_map = {
                '招牌': ['牛肉面条', '扬州炒饭(米饭)', '经典汉堡', '意式披萨'],
                '小吃': ['香酥炸鸡', '日式寿司', '健康沙拉'],
                '饮品': ['美式咖啡', '草莓蛋糕', '珍珠奶茶']
            }
            
            for cat_name, dishes in categories_map.items():
                category, _ = Category.objects.get_or_create(shop=shop, name=cat_name)
                
                # 每个分类随机选几个菜
                selected_dishes = random.sample(dishes, random.randint(1, 3))
                
                for dish_name in selected_dishes:
                    full_name = f"{dish_name}"
                    Dish.objects.get_or_create(
                        shop=shop,
                        category=category,
                        name=full_name,
                        defaults={
                            'price': random.randint(15, 88),
                            'original_price': random.randint(90, 120) if random.random() > 0.7 else None,
                            'description': f"精选食材制作的{full_name}。",
                            'image_url': get_image_for_dish(dish_name),
                            'stock': 100,
                            'tag': random.choice(['daily_deal', 'flash_sale', 'big_brand', None])
                        }
                    )

    # 4. 创建特定演示账号
    print("生成特定演示账号...")
    
    # 骑手: rider
    rider, created = User.objects.get_or_create(username='rider', defaults={
        'email': 'rider@example.com',
        'role': 'rider'
    })
    if created:
        rider.set_password('password123')
        rider.save()
        print("  - 骑手: rider (密码: password123)")

    # 商家: mcd_boss (麦当劳)
    mcd_boss, created = User.objects.get_or_create(username='mcd_boss', defaults={
        'email': 'mcd_boss@example.com',
        'role': 'merchant'
    })
    if created:
        mcd_boss.set_password('password123')
        mcd_boss.save()
        
        # 创建麦当劳店铺 (北京)
        Shop.objects.get_or_create(merchant=mcd_boss, defaults={
            'name': '麦当劳 (McDonalds) - 北京三里屯',
            'description': '我就喜欢 (I\'m lovin\' it)',
            'address': '北京市朝阳区三里屯路19号',
            'latitude': 39.935,
            'longitude': 116.455,
            'rating': 4.8,
            'image_url': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop'
        })
        print("  - 商家: mcd_boss (密码: password123)")

    # 商家: mcd_beijing_new (北京朝阳新店)
    mcd_bj_new, created = User.objects.get_or_create(username='mcd_beijing_new', defaults={
        'email': 'mcd_bj_new@example.com',
        'role': 'merchant'
    })
    if created:
        mcd_bj_new.set_password('password123')
        mcd_bj_new.save()
        
        # 创建麦当劳店铺 (北京朝阳)
        # 朝阳公园附近: 39.94, 116.48
        Shop.objects.get_or_create(merchant=mcd_bj_new, defaults={
            'name': '麦当劳 (McDonalds) - 北京朝阳公园店',
            'description': '全新形象店，美味升级',
            'address': '北京市朝阳区朝阳公园路',
            'latitude': 39.942,
            'longitude': 116.485,
            'rating': 4.7,
            'image_url': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop'
        })
        print("  - 商家: mcd_beijing_new (密码: password123)")

    # 商家: mcd_ningbo (宁波麦当劳)
    mcd_ningbo_user, created = User.objects.get_or_create(username='mcd_ningbo', defaults={
        'email': 'mcd_ningbo@example.com',
        'role': 'merchant'
    })
    if created:
        mcd_ningbo_user.set_password('password123')
        mcd_ningbo_user.save()
        
        # 创建麦当劳店铺 (宁波镇海)
        # 镇海大致坐标: 29.95, 121.71
        Shop.objects.get_or_create(merchant=mcd_ningbo_user, defaults={
            'name': '麦当劳 (McDonalds) - 宁波镇海店',
            'description': '宁波镇海旗舰店，24小时营业',
            'address': '宁波市镇海区骆驼街道',
            'latitude': 29.955,
            'longitude': 121.715,
            'rating': 4.9,
            'image_url': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop'
        })
        print("  - 商家: mcd_ningbo (密码: password123)")

    # 顾客: custom
    customer, created = User.objects.get_or_create(username='custom', defaults={
        'email': 'custom@example.com',
        'role': 'customer'
    })
    if created:
        customer.set_password('password123')
        customer.save()
        print("  - 顾客: custom (密码: password123)")

    print("分布数据生成完毕！")

if __name__ == '__main__':
    create_initial_data()
