#!/usr/bin/env python
"""
Verificação completa do sistema social Mark Foot
"""
import sys
import os

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')

import django
django.setup()

from django.contrib.auth.models import User
from social.models import Comment, UserFollow, UserActivity, CommentLike, Notification, CommentReport
from core.models import Match

def verificar_sistema():
    print("🔍 VERIFICAÇÃO DO SISTEMA SOCIAL MARK FOOT")
    print("=" * 50)
    
    # 1. Verificar modelos
    print("\n📊 VERIFICAÇÃO DOS MODELOS:")
    modelos = [
        (Comment, "Comentários"),
        (UserFollow, "Relacionamentos"),
        (UserActivity, "Atividades"),
        (CommentLike, "Likes"),
        (Notification, "Notificações"),
        (CommentReport, "Denúncias")
    ]
    
    for modelo, nome in modelos:
        count = modelo.objects.count()
        print(f"  ✅ {nome}: {count} registros")
    
    # 2. Verificar dados base
    print("\n📋 DADOS BASE:")
    users_count = User.objects.count()
    matches_count = Match.objects.count()
    print(f"  👤 Usuários: {users_count}")
    print(f"  ⚽ Partidas: {matches_count}")
    
    # 3. Verificar comentários por status
    print("\n💬 COMENTÁRIOS POR STATUS:")
    for status, label in Comment.STATUS_CHOICES:
        count = Comment.objects.filter(status=status).count()
        print(f"  📝 {label}: {count}")
    
    # 4. Verificar usuários mais ativos
    print("\n🏆 TOP 5 USUÁRIOS MAIS ATIVOS:")
    from django.db.models import Count
    top_users = User.objects.annotate(
        comment_count=Count('comment')
    ).filter(comment_count__gt=0).order_by('-comment_count')[:5]
    
    for i, user in enumerate(top_users, 1):
        print(f"  {i}. {user.username}: {user.comment_count} comentários")
    
    # 5. Verificar relacionamentos
    print("\n🤝 REDE SOCIAL:")
    follows = UserFollow.objects.count()
    users_with_followers = User.objects.filter(followers__isnull=False).distinct().count()
    users_following = User.objects.filter(following__isnull=False).distinct().count()
    
    print(f"  🔗 Total de relacionamentos: {follows}")
    print(f"  👥 Usuários com seguidores: {users_with_followers}")
    print(f"  👤 Usuários seguindo outros: {users_following}")
    
    # 6. Verificar atividades recentes
    print("\n🕒 ATIVIDADES RECENTES (últimas 5):")
    recent_activities = UserActivity.objects.order_by('-created_at')[:5]
    for activity in recent_activities:
        print(f"  📌 {activity.user.username}: {activity.description}")
    
    print("\n" + "=" * 50)
    print("✅ VERIFICAÇÃO CONCLUÍDA - SISTEMA FUNCIONANDO!")

if __name__ == "__main__":
    verificar_sistema()
