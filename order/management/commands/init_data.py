from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from order.models import UserProfile, Merchant, Category, Dish

class Command(BaseCommand):
    help = 'Initialize sample data for the ordering system'

    def handle(self, *args, **options):
        # 创建分类
        categories_data = [
            {'name': '主食', 'description': '米饭、面条等主食'},
            {'name': '小吃', 'description': '各种小吃'},
            {'name': '饮料', 'description': '饮品'},
            {'name': '套餐', 'description': '优惠套餐'},
            {'name': '汤类', 'description': '各种汤品'},
            {'name': '甜点', 'description': '甜品点心'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(**cat_data)
            categories[cat_data['name']] = category
        
        # 创建多个商家
        merchants_data = [
            {
                'username': 'merchant1',
                'store_name': '美味中餐厅',
                'description': '提供正宗川菜、湘菜等各地美食',
                'address': '学校东门美食街1号',
                'phone': '13800138001',
                'dishes': [
                    {'name': '宫保鸡丁', 'price': 28.00, 'description': '经典川菜，麻辣鲜香', 'category': '主食'},
                    {'name': '麻婆豆腐', 'price': 22.00, 'description': '麻辣鲜香，下饭神器', 'category': '主食'},
                    {'name': '水煮鱼', 'price': 38.00, 'description': '鲜嫩鱼肉，麻辣过瘾', 'category': '主食'},
                    {'name': '米饭', 'price': 2.00, 'description': '香喷喷的白米饭', 'category': '主食'},
                    {'name': '酸梅汤', 'price': 8.00, 'description': '冰镇酸梅汤', 'category': '饮料'},
                ]
            },
            {
                'username': 'merchant2', 
                'store_name': '西式快餐店',
                'description': '提供汉堡、披萨等西式快餐',
                'address': '学校西门商业区2号',
                'phone': '13800138002',
                'dishes': [
                    {'name': '经典汉堡', 'price': 25.00, 'description': '牛肉汉堡配蔬菜', 'category': '主食'},
                    {'name': '鸡肉卷', 'price': 18.00, 'description': '香脆鸡肉卷', 'category': '主食'},
                    {'name': '薯条', 'price': 12.00, 'description': '金黄酥脆的薯条', 'category': '小吃'},
                    {'name': '可乐', 'price': 6.00, 'description': '冰镇可乐', 'category': '饮料'},
                    {'name': '冰淇淋', 'price': 8.00, 'description': '香草冰淇淋', 'category': '甜点'},
                ]
            },
            {
                'username': 'merchant3',
                'store_name': '日料寿司店',
                'description': '新鲜寿司、刺身等日式料理',
                'address': '学校南门美食广场3号',
                'phone': '13800138003',
                'dishes': [
                    {'name': '三文鱼寿司', 'price': 15.00, 'description': '新鲜三文鱼寿司', 'category': '主食'},
                    {'name': '金枪鱼寿司', 'price': 16.00, 'description': '优质金枪鱼寿司', 'category': '主食'},
                    {'name': '天妇罗', 'price': 28.00, 'description': '日式炸虾天妇罗', 'category': '小吃'},
                    {'name': '味增汤', 'price': 8.00, 'description': '传统日式味增汤', 'category': '汤类'},
                    {'name': '绿茶', 'price': 5.00, 'description': '日式煎茶', 'category': '饮料'},
                ]
            },
            {
                'username': 'merchant4',
                'store_name': '奶茶甜品屋',
                'description': '各种奶茶、果汁和甜点',
                'address': '学校北门步行街4号',
                'phone': '13800138004',
                'dishes': [
                    {'name': '珍珠奶茶', 'price': 12.00, 'description': '经典珍珠奶茶', 'category': '饮料'},
                    {'name': '水果茶', 'price': 15.00, 'description': '新鲜水果茶', 'category': '饮料'},
                    {'name': '芝士蛋糕', 'price': 18.00, 'description': '浓郁芝士蛋糕', 'category': '甜点'},
                    {'name': '提拉米苏', 'price': 20.00, 'description': '意式提拉米苏', 'category': '甜点'},
                    {'name': '布丁', 'price': 10.00, 'description': '香甜布丁', 'category': '甜点'},
                ]
            }
        ]
        
        for merchant_data in merchants_data:
            user, created = User.objects.get_or_create(
                username=merchant_data['username'],
                defaults={'email': f'{merchant_data["username"]}@example.com'}
            )
            if created:
                user.set_password('password123')
                user.save()
            
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'merchant'}
            )
            
            merchant, created = Merchant.objects.get_or_create(
                user_profile=profile,
                defaults={
                    'store_name': merchant_data['store_name'],
                    'description': merchant_data['description'],
                    'address': merchant_data['address'],
                    'phone': merchant_data['phone']
                }
            )
            
            # 创建菜品
            for dish_data in merchant_data['dishes']:
                Dish.objects.get_or_create(
                    merchant=merchant,
                    name=dish_data['name'],
                    defaults={
                        'price': dish_data['price'],
                        'description': dish_data['description'],
                        'category': categories[dish_data['category']]
                    }
                )
        
        # 创建一个测试顾客账号
        customer_user, created = User.objects.get_or_create(
            username='customer1',
            defaults={'email': 'customer1@example.com'}
        )
        if created:
            customer_user.set_password('password123')
            customer_user.save()
            UserProfile.objects.create(user=customer_user, role='customer')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized sample data')
        )
        self.stdout.write('商家测试账号:')
        for merchant_data in merchants_data:
            self.stdout.write(f'  {merchant_data["username"]} / password123')
        self.stdout.write('顾客测试账号: customer1 / password123')