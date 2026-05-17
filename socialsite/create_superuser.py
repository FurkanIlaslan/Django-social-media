#!/usr/bin/env python
"""
Otomatik superuser oluşturma scripti
Render.com free tier için (Shell erişimi yok)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialsite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Admin bilgileri
username = 'admin'
email = 'admin@socialsite.com'
password = 'Admin123!'

# Eğer admin yoksa oluştur
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Admin',
        last_name='User'
    )
    print(f'✅ Superuser created successfully!')
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'Email: {email}')
else:
    print(f'⚠️  Superuser "{username}" already exists.')
