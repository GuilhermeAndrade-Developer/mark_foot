#!/usr/bin/env python3
"""
Script para testar autenticação dos usuários.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def test_authentication():
    print('=== TESTE DE AUTENTICAÇÃO ===')
    
    # Testar usuário comum
    print('\n🧪 Testando usuário comum (testuser):')
    test_user = User.objects.get(username='testuser')
    print(f'   Username: {test_user.username}')
    print(f'   Email: {test_user.email}')
    print(f'   Is active: {test_user.is_active}')
    print(f'   Is superuser: {test_user.is_superuser}')
    
    auth_test = authenticate(username='testuser', password='test123')
    check_pass = test_user.check_password('test123')
    print(f'   Authenticate result: {auth_test}')
    print(f'   Check password: {check_pass}')
    
    # Testar administrador
    print('\n🔐 Testando administrador (admin):')
    admin_user = User.objects.get(username='admin')
    print(f'   Username: {admin_user.username}')
    print(f'   Email: {admin_user.email}')
    print(f'   Is active: {admin_user.is_active}')
    print(f'   Is superuser: {admin_user.is_superuser}')
    
    auth_admin = authenticate(username='admin', password='admin123')
    check_admin_pass = admin_user.check_password('admin123')
    print(f'   Authenticate result: {auth_admin}')
    print(f'   Check password: {check_admin_pass}')
    print(f'   Password hash: {admin_user.password[:50]}...')
    
    # Resetar senha do admin se necessário
    if not check_admin_pass:
        print('\n🔧 Resetando senha do admin...')
        admin_user.set_password('admin123')
        admin_user.save()
        
        # Testar novamente
        auth_admin_new = authenticate(username='admin', password='admin123')
        print(f'   Nova autenticação: {auth_admin_new}')

if __name__ == '__main__':
    test_authentication()
