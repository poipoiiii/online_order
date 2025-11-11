# Online_order/production.py
import os
from .settings import *

# 生产环境配置
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# 静态文件配置
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# 时区设置
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

# Session配置
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False  # 开发环境设为False
SESSION_COOKIE_HTTPONLY = True

# 安全设置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-here')

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}