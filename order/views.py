import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                profile = UserProfile.objects.get(user=user)
                return JsonResponse({
                    'success': True, 
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': profile.role
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': '用户名或密码错误'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': '无效请求'})

@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            role = data.get('role', 'customer')
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': '用户名已存在'})
            
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username, 
                    password=password, 
                    email=email
                )
                profile = UserProfile.objects.create(
                    user=user,
                    role=role
                )
                
                if role == 'merchant':
                    Merchant.objects.create(
                        user_profile=profile,
                        store_name=data.get('store_name', f"{username}的店铺"),
                        description=data.get('description', ''),
                        address=data.get('address', ''),
                        phone=data.get('phone', '')
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': '无效请求'})

@csrf_exempt
@login_required
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})

@login_required
def api_user_info(request):
    profile = UserProfile.objects.get(user=request.user)
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'role': profile.role
    }
    
    if profile.role == 'merchant':
        merchant = Merchant.objects.get(user_profile=profile)
        user_data['merchant'] = {
            'id': merchant.id,
            'store_name': merchant.store_name,
            'description': merchant.description
        }
    
    return JsonResponse({'user': user_data})

def api_merchants(request):
    merchants = Merchant.objects.filter(is_active=True)
    merchants_data = []
    for merchant in merchants:
        merchants_data.append({
            'id': merchant.id,
            'store_name': merchant.store_name,
            'description': merchant.description,
            'address': merchant.address,
            'phone': merchant.phone
        })
    return JsonResponse({'merchants': merchants_data})

def api_merchant_dishes(request, merchant_id):
    try:
        merchant = Merchant.objects.get(id=merchant_id)
        dishes = Dish.objects.filter(merchant=merchant, is_available=True)
        dishes_data = []
        for dish in dishes:
            dishes_data.append({
                'id': dish.id,
                'name': dish.name,
                'description': dish.description,
                'price': str(dish.price),
                'category': dish.category.name if dish.category else '未分类',
               # 'image': dish.image.url if dish.image else None
                'is_available': dish.is_available 
            })
        return JsonResponse({
            'merchant': {
                'id': merchant.id,
                'store_name': merchant.store_name
            },
            'dishes': dishes_data
        })
    except Merchant.DoesNotExist:
        return JsonResponse({'error': '商家不存在'}, status=404)

@csrf_exempt
@login_required
def api_merchant_manage_dishes(request):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'})
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'merchant':
            return JsonResponse({'error': '无权限'}, status=403)
        
        merchant = Merchant.objects.get(user_profile=profile)
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'add':
            dish = Dish.objects.create(
                merchant=merchant,
                name=data.get('name'),
                description=data.get('description', ''),
                price=data.get('price'),
                is_available=data.get('is_available', True)
            )
            return JsonResponse({'success': True, 'dish_id': dish.id})
        
        elif action == 'update':
            dish = Dish.objects.get(id=data.get('id'), merchant=merchant)
            dish.name = data.get('name', dish.name)
            dish.description = data.get('description', dish.description)
            dish.price = data.get('price', dish.price)
            dish.is_available = data.get('is_available', dish.is_available)
            dish.save()
            return JsonResponse({'success': True})
        
        elif action == 'delete':
            dish = Dish.objects.get(id=data.get('id'), merchant=merchant)
            dish.delete()
            return JsonResponse({'success': True})
        
        elif action == 'list':
            dishes = Dish.objects.filter(merchant=merchant)
            dishes_data = []
            for dish in dishes:
                dishes_data.append({
                    'id': dish.id,
                    'name': dish.name,
                    'description': dish.description,
                    'price': str(dish.price),
                    'is_available': dish.is_available
                })
            return JsonResponse({'dishes': dishes_data})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def api_create_order(request):
    if request.method == 'POST':
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role != 'customer':
                return JsonResponse({'error': '只有顾客可以下单'}, status=403)
            
            data = json.loads(request.body)
            merchant_id = data.get('merchant_id')
            items = data.get('items', [])
            notes = data.get('notes', '')
            
            merchant = Merchant.objects.get(id=merchant_id)
            
            with transaction.atomic():
                total_amount = 0
                order_items = []
                
                for item in items:
                    dish = Dish.objects.get(id=item['dish_id'])
                    quantity = item['quantity']
                    item_total = dish.price * quantity
                    total_amount += item_total
                    
                    order_items.append(OrderItem(
                        dish=dish,
                        quantity=quantity,
                        price=dish.price
                    ))
                
                order = Order.objects.create(
                    customer=profile,
                    merchant=merchant,  # 确保这里正确设置了商家
                    total_amount=total_amount,
                    customer_notes=notes
                )
                
                for order_item in order_items:
                    order_item.order = order
                    order_item.save()
            
            return JsonResponse({'success': True, 'order_id': order.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
def api_user_orders(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if profile.role == 'customer':
        orders = Order.objects.filter(customer=profile).order_by('-created_at')
    else:
        merchant = Merchant.objects.get(user_profile=profile)
        orders = Order.objects.filter(merchant=merchant).order_by('-created_at')
    
    orders_data = []
    for order in orders:
        order_data = {
            'id': order.id,
            'total_amount': str(order.total_amount),
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M'),
            'merchant': { 
                'id': order.merchant.id,
                'store_name': order.merchant.store_name
            },
            'items': []
        }
        
        for item in order.items.all():
            order_data['items'].append({
                'dish_name': item.dish.name,
                'quantity': item.quantity,
                'price': str(item.price)
            })
        
        orders_data.append(order_data)
    
    return JsonResponse({'orders': orders_data})

@csrf_exempt
@login_required
def api_update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role != 'merchant':
                return JsonResponse({'error': '只有商家可以更新订单状态'}, status=403)
            
            merchant = Merchant.objects.get(user_profile=profile)
            order = Order.objects.get(id=order_id, merchant=merchant)
            
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': '无效的状态'}, status=400)
                
        except Order.DoesNotExist:
            return JsonResponse({'error': '订单不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': '无效请求'})

@csrf_exempt
@login_required
def api_merchant_orders(request):
    """商家获取订单的API"""
    if request.method == 'POST':
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role != 'merchant':
                return JsonResponse({'error': '无权限'}, status=403)
            
            merchant = Merchant.objects.get(user_profile=profile)
            orders = Order.objects.filter(merchant=merchant).order_by('-created_at')
            
            orders_data = []
            for order in orders:
                order_data = {
                    'id': order.id,
                    'order_number': f"ORD{order.id:06d}",
                    'total_amount': str(order.total_amount),
                    'status': order.status,
                    'status_display': order.get_status_display(),
                    'created_at': timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                    'customer_name': order.customer.user.username,  # 直接返回用户名
                    'customer_notes': order.customer_notes,
                    'items': []
                }
                
                for item in order.items.all():  # 正确的关联名称 # 注意：这里应该是 order_items
                    order_data['items'].append({
                        'dish_name': item.dish.name,
                        'quantity': item.quantity,
                        'price': str(item.price),
                        'subtotal': str(item.price * item.quantity)
                    })
                
                orders_data.append(order_data)
            
            return JsonResponse({'success': True, 'orders': orders_data})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': '无效请求'})




# 页面视图
def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def customer_home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    return render(request, 'customer_home.html')

def merchant_home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    return render(request, 'merchant_home.html')

def customer_merchant(request, merchant_id):
    return render(request, 'customer_merchant.html')

def customer_orders(request):
    return render(request, 'customer_orders.html')


def merchant_orders(request):
    return render(request, 'merchant_orders.html')

# 重定向根路径到登录页
def index(request):
    return render(request, 'login.html')














