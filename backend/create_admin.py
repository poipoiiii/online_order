import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery.settings')
django.setup()

from core.models import User

def create_admin():
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpassword123'
    
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        User.objects.create_superuser(username=username, email=email, password=password, role='admin')
        print(f"Superuser created successfully.")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == '__main__':
    create_admin()
