import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from social.models import SocialPlatform, PrivateGroup
print(f'Plataformas criadas: {SocialPlatform.objects.count()}')
print(f'Grupos criados: {PrivateGroup.objects.count()}')

if SocialPlatform.objects.exists():
    platform = SocialPlatform.objects.first()
    print(f'Primeira plataforma: {platform.display_name}')

if PrivateGroup.objects.exists():
    group = PrivateGroup.objects.first()
    print(f'Primeiro grupo: {group.name}')
