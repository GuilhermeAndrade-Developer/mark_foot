#!/usr/bin/env python3
"""
Script para criar usuários de teste no sistema.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    print('=== VERIFICANDO USUÁRIOS EXISTENTES ===')
    
    # Verificar usuários existentes
    users = User.objects.all()
    if users.exists():
        print('Usuários encontrados:')
        for user in users:
            print(f'- Username: {user.username}, Email: {user.email}, Superuser: {user.is_superuser}')
    else:
        print('Nenhum usuário encontrado no sistema.')
    
    print('\n=== CRIANDO USUÁRIOS DE TESTE ===')
    
    # Criar superusuário se não existir
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@markfoot.com',
            password='admin123'
        )
        print('✅ SUPERUSUÁRIO CRIADO:')
        print('   Username: admin')
        print('   Password: admin123')
        print('   Email: admin@markfoot.com')
    else:
        print('ℹ️  Superusuário "admin" já existe')
    
    # Criar usuário de teste se não existir
    if not User.objects.filter(username='testuser').exists():
        test_user = User.objects.create_user(
            username='testuser',
            email='test@markfoot.com',
            password='test123'
        )
        print('✅ USUÁRIO DE TESTE CRIADO:')
        print('   Username: testuser')
        print('   Password: test123')
        print('   Email: test@markfoot.com')
    else:
        print('ℹ️  Usuário de teste "testuser" já existe')
    
    print('\n=== RESUMO DAS CREDENCIAIS ===')
    print('🔑 ADMINISTRADOR:')
    print('   URL: http://localhost:8001/admin/')
    print('   Username: admin')
    print('   Password: admin123')
    print('')
    print('👤 USUÁRIO COMUM:')
    print('   Username: testuser')
    print('   Password: test123')

if __name__ == '__main__':
    main()
