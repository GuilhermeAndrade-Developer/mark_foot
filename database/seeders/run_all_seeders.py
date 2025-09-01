#!/usr/bin/env python3
"""
Script auxiliar para executar todos os seeders disponíveis
"""

import os
import sys
import subprocess
import django

# Add the project root to Python path
sys.path.append('/app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

def run_all_seeders():
    """Execute todos os seeders em ordem"""
    
    print("🌱 Executando todos os seeders do Mark Foot...")
    print("=" * 60)
    
    # Lista de seeders em ordem de dependência
    seeders = [
        ('seed_users.py', 'Usuários base'),
        ('seed_core_data.py', 'Times, jogadores e competições (Django command)'),
        ('seed_billing_data.py', 'Planos de assinatura e faturamento'),
        ('seed_user_data.py', 'Perfis de usuário, seguidos e atividades'),
        ('seed_seasons_standings.py', 'Temporadas e classificações'),
        ('seed_player_data.py', 'Estatísticas e transferências de jogadores'),
        ('seed_api_data.py', 'Logs de API e sincronização'),
        ('seed_content_data.py', 'Conteúdo e artigos (Django command)'),
        ('seed_polls_data.py', 'Enquetes (Django command)'),
        ('seed_social_data.py', 'Dados sociais (Django command)'),
        ('seed_gamification_data.py', 'Gamificação (Django command)'),
        ('seed_forum_data.py', 'Fórum (Django command)'),
        ('seed_chat_data.py', 'Chat (Django command)'),
        ('seed_social_sharing_data.py', 'Compartilhamento social'),
        ('seed_whatsapp_data.py', 'WhatsApp Integration'),
        ('seed_ai_data.py', 'Dados de IA (Django command)'),
        ('seed_business_data.py', 'Business dashboard (Django command)')
    ]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for seeder_file, description in seeders:
        print(f"\n🔧 Executando: {description}")
        print("-" * 50)
        
        seeder_path = os.path.join(current_dir, seeder_file)
        
        try:
            if '(Django command)' in description:
                # É um comando Django, execute via manage.py
                command_name = seeder_file.replace('seed_', '').replace('.py', '')
                if command_name == 'core_data':
                    result = subprocess.run([
                        'python', '/app/manage.py', 'seed_core_data', '--quick'
                    ], cwd='/app', capture_output=True, text=True, timeout=300)
                else:
                    result = subprocess.run([
                        'python', '/app/manage.py', f'seed_{command_name}'
                    ], cwd='/app', capture_output=True, text=True, timeout=300)
            elif os.path.exists(seeder_path):
                # É um script Python standalone
                result = subprocess.run([
                    'python', seeder_path
                ], cwd='/app', capture_output=True, text=True, timeout=300)
            else:
                print(f"  ⚠️  Seeder não encontrado: {seeder_path}")
                continue
            
            if result.returncode == 0:
                print(f"  ✅ {description} - Sucesso!")
                if result.stdout:
                    # Mostrar apenas linhas importantes do output
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-3:]:  # Últimas 3 linhas
                        if line.strip() and ('✅' in line or '📊' in line or 'Summary' in line):
                            print(f"     {line}")
            else:
                print(f"  ❌ {description} - Falhou!")
                if result.stderr:
                    print(f"     Erro: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {description} - Timeout (>5 min)")
        except Exception as e:
            print(f"  ❌ {description} - Erro: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Execução de seeders concluída!")
    print("   Verifique os resultados acima para confirmar se tudo foi executado corretamente.")


if __name__ == '__main__':
    run_all_seeders()
