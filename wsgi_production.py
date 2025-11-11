# wsgi_production.py（与manage.py同级）
import os
import sys
from waitress import serve

# 添加项目路径到Python路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# 设置生产环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_order.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

if __name__ == '__main__':
    print("=" * 50)
    print("网上订餐系统 - 生产服务器")
    print("访问地址: http://127.0.0.1:8000")
    print("支持多用户同时访问")
    print("=" * 50)
    
    # 启动Waitress生产服务器
    serve(
        application,
        host='0.0.0.0',    # 允许所有IP访问
        port=8000,
        threads=8,         # 线程数
        channel_timeout=300
    )