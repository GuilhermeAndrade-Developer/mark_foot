#!/usr/bin/env python3
"""
Script completo de teste de autenticação para a plataforma Mark Foot.
"""
import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.contrib.auth.models import User

def test_api_login(username, password):
    """Testa login via API REST."""
    url = 'http://localhost:8001/api/v1/auth/login/'
    data = {
        'username': username,
        'password': password
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            return True, tokens
        else:
            return False, response.json()
    except Exception as e:
        return False, str(e)

def main():
    print('=' * 60)
    print('🧪 TESTE COMPLETO DE AUTENTICAÇÃO - MARK FOOT')
    print('=' * 60)
    
    # Verificar usuários existentes
    print('\n📋 USUÁRIOS CADASTRADOS:')
    users = User.objects.all()
    for user in users:
        status = "🟢 Ativo" if user.is_active else "🔴 Inativo"
        tipo = "👑 Administrador" if user.is_superuser else "👤 Usuário comum"
        print(f'   {tipo} - {user.username} ({user.email}) - {status}')
    
    print('\n🔐 TESTES DE LOGIN VIA API REST:')
    
    # Teste 1: Login do administrador
    print('\n1. Testando login do ADMINISTRADOR:')
    success, result = test_api_login('admin', 'admin123')
    if success:
        print('   ✅ Login do admin SUCESSO!')
        print('   🎟️  Access Token recebido')
        print('   🔄 Refresh Token recebido')
    else:
        print('   ❌ Login do admin FALHOU!')
        print(f'   💬 Erro: {result}')
    
    # Teste 2: Login do usuário comum
    print('\n2. Testando login do USUÁRIO COMUM:')
    success, result = test_api_login('testuser', 'test123')
    if success:
        print('   ✅ Login do usuário comum SUCESSO!')
        print('   🎟️  Access Token recebido')
        print('   🔄 Refresh Token recebido')
    else:
        print('   ❌ Login do usuário comum FALHOU!')
        print(f'   💬 Erro: {result}')
    
    # Teste 3: Login com credenciais inválidas
    print('\n3. Testando login com credenciais INVÁLIDAS:')
    success, result = test_api_login('wronguser', 'wrongpass')
    if not success:
        print('   ✅ Rejeição de credenciais inválidas FUNCIONANDO!')
        print(f'   💬 Mensagem: {result}')
    else:
        print('   ❌ PROBLEMA: Credenciais inválidas foram aceitas!')
    
    print('\n' + '=' * 60)
    print('📚 RESUMO DAS CREDENCIAIS PARA USO:')
    print('=' * 60)
    
    print('\n👑 ADMINISTRADOR (Acesso completo):')
    print('   🌐 URL Admin: http://localhost:8001/admin/')
    print('   🆔 Username: admin')
    print('   🔑 Password: admin123')
    print('   📧 Email: admin@markfoot.com')
    
    print('\n👤 USUÁRIO COMUM (API REST):')
    print('   🌐 URL API: http://localhost:8001/api/v1/auth/login/')
    print('   🆔 Username: testuser')
    print('   🔑 Password: test123')
    print('   📧 Email: test@markfoot.com')
    
    print('\n🔗 ENDPOINTS IMPORTANTES:')
    print('   🏠 API Root: http://localhost:8001/api/v1/')
    print('   🔐 Login: http://localhost:8001/api/v1/auth/login/')
    print('   🔄 Refresh: http://localhost:8001/api/v1/auth/refresh/')
    print('   ⚙️  Admin: http://localhost:8001/admin/')
    print('   🎯 Frontend: http://localhost:3000/')
    
    print('\n' + '=' * 60)
    print('✅ TESTE DE AUTENTICAÇÃO CONCLUÍDO!')
    print('=' * 60)

if __name__ == '__main__':
    main()
