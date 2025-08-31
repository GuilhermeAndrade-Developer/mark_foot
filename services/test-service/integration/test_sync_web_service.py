#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from core.models import Competition
from django.core.management import call_command

print("🔍 Verificando competições no banco de dados:")
competitions = Competition.objects.all()
for comp in competitions:
    print(f"  {comp.code}: {comp.name}")

print(f"\nTotal de competições: {competitions.count()}")

if competitions.count() == 0:
    print("\n❌ Nenhuma competição encontrada no banco!")
    print("💡 Execute o comando 'python manage.py test_api' primeiro para criar as competições.")
else:
    # Testar uma competição específica
    try:
        print("\n🔄 Testando sincronização da PL...")
        call_command('sync_competition', 'PL', season='2024', limit_matches=5)
        print("✅ Sincronização da PL funcionou!")
    except Exception as e:
        print(f"❌ Erro na sincronização da PL: {str(e)}")
        import traceback
        print(traceback.format_exc())
