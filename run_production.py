# run_production.py（与manage.py同级）
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # 设置生产环境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Online_order.production")
    
    # 添加项目路径
    project_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_path)
    
    # 导入并运行
    from wsgi_production import application
    from waitress import serve
    
    print("启动网上订餐系统生产服务器...")
    serve(application, host='0.0.0.0', port=8000, threads=8)