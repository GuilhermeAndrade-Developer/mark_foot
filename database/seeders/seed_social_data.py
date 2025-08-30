"""
Seeder for social module data.
Creates professional development data replacing hardcoded social features.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.models import (
    SocialPlatform, ShareTemplate, PrivateGroup, GroupMembership,
    UserFollow, UserActivity, Post, Comment
)
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed social data for development'

    def handle(self, *args, **options):
        self.stdout.write('👥 Seeding social data...')
        
        # Create social platforms
        platforms_created = self.create_platforms()
        
        # Create share templates
        templates_created = self.create_templates()
        
        # Create groups
        groups_created = self.create_groups()
        
        # Create social interactions
        follows_created = self.create_follows()
        posts_created = self.create_posts()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Social data seeded:\n'
                f'   📱 Platforms: {platforms_created}\n'
                f'   📝 Templates: {templates_created}\n'
                f'   👥 Groups: {groups_created}\n'
                f'   🔗 Follows: {follows_created}\n'
                f'   📮 Posts: {posts_created}'
            )
        )

    def create_platforms(self):
        """Create social media platforms"""
        platforms_data = [
            {
                'name': 'twitter',
                'display_name': 'Twitter/X',
                'character_limit': 280,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://twitter.com',
                'is_active': True
            },
            {
                'name': 'instagram',
                'display_name': 'Instagram',
                'character_limit': 2200,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://instagram.com',
                'is_active': True
            },
            {
                'name': 'tiktok',
                'display_name': 'TikTok',
                'character_limit': 2200,
                'supports_images': False,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://tiktok.com',
                'is_active': True
            },
            {
                'name': 'facebook',
                'display_name': 'Facebook',
                'character_limit': 63206,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://facebook.com',
                'is_active': True
            },
            {
                'name': 'linkedin',
                'display_name': 'LinkedIn',
                'character_limit': 3000,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://linkedin.com',
                'is_active': True
            }
        ]

        created_count = 0
        for platform_data in platforms_data:
            platform, created = SocialPlatform.objects.get_or_create(
                name=platform_data['name'],
                defaults=platform_data
            )
            if created:
                created_count += 1

        return created_count

    def create_templates(self):
        """Create share templates"""
        platforms = {p.name: p for p in SocialPlatform.objects.all()}
        
        templates_data = [
            # Twitter templates
            {
                'platform_name': 'twitter',
                'name': 'Resultado de Jogo - Twitter',
                'template_type': 'match_result',
                'title_template': '⚽ {home_team} vs {away_team}',
                'content_template': '🔥 FINAL: {home_team} {home_score} - {away_score} {away_team}\n\n{match_summary}\n\n#Futebol #MarkFoot #{home_team_slug} #{away_team_slug}',
                'hashtags': '#Futebol #MarkFoot #Resultado',
                'available_variables': ['home_team', 'away_team', 'home_score', 'away_score', 'match_summary', 'home_team_slug', 'away_team_slug']
            },
            {
                'platform_name': 'twitter',
                'name': 'Estatísticas - Twitter',
                'template_type': 'player_stat',
                'title_template': '📊 {player_name}',
                'content_template': '⭐ {player_name} em grande forma!\n\n📈 Stats:\n⚽ {goals} gols\n🎯 {assists} assistências\n💯 {rating}/10\n\n#Futebol #MarkFoot #{team_slug}',
                'hashtags': '#Futebol #MarkFoot #Stats',
                'available_variables': ['player_name', 'goals', 'assists', 'rating', 'team_slug']
            },
            
            # Instagram templates
            {
                'platform_name': 'instagram',
                'name': 'Resultado de Jogo - Instagram',
                'template_type': 'match_result',
                'title_template': '🔥 {home_team} vs {away_team}',
                'content_template': '⚽ QUE JOGO! {home_team} {home_score} - {away_score} {away_team}\n\n{match_summary}\n\n🏆 {competition_name}\n📅 {match_date}\n🏟️ {stadium}\n\nO que acharam? 👇\n\n#Futebol #MarkFoot #{home_team_slug} #{away_team_slug}',
                'hashtags': '#Futebol #MarkFoot #Resultado',
                'available_variables': ['home_team', 'away_team', 'home_score', 'away_score', 'match_summary', 'competition_name', 'match_date', 'stadium', 'home_team_slug', 'away_team_slug']
            }
        ]

        created_count = 0
        for template_data in templates_data:
            if template_data['platform_name'] not in platforms:
                continue
                
            platform = platforms[template_data['platform_name']]
            template_data_clean = {k: v for k, v in template_data.items() if k != 'platform_name'}
            template_data_clean['platform'] = platform
            
            template, created = ShareTemplate.objects.get_or_create(
                name=template_data['name'],
                platform=platform,
                defaults=template_data_clean
            )
            if created:
                created_count += 1

        return created_count

    def create_groups(self):
        """Create sample private groups"""
        users = list(User.objects.filter(is_active=True))
        if not users:
            return 0

        groups_data = [
            {
                'name': 'Torcedores do Flamengo',
                'description': 'Grupo oficial dos torcedores do Mengão',
                'group_type': 'team_fans',
                'privacy_level': 'public',
                'max_members': 1000,
                'allow_member_invites': True,
                'require_admin_approval': False
            },
            {
                'name': 'Família Palmeirense',
                'description': 'Grupo da família para torcedores do Palmeiras',
                'group_type': 'family',
                'privacy_level': 'private',
                'max_members': 50,
                'allow_member_invites': True,
                'require_admin_approval': True
            },
            {
                'name': 'Analistas Táticos',
                'description': 'Discussões profundas sobre táticas no futebol',
                'group_type': 'custom',
                'privacy_level': 'restricted',
                'max_members': 100,
                'allow_member_invites': False,
                'require_admin_approval': True
            },
            {
                'name': 'Brasileirão 2024',
                'description': 'Tudo sobre o Campeonato Brasileiro',
                'group_type': 'competition',
                'privacy_level': 'public',
                'max_members': 500,
                'allow_member_invites': True,
                'require_admin_approval': False
            },
            {
                'name': 'Amigos do Futebol',
                'description': 'Bate-papo geral sobre futebol',
                'group_type': 'friends',
                'privacy_level': 'restricted',
                'max_members': 200,
                'allow_member_invites': True,
                'require_admin_approval': False
            }
        ]

        created_count = 0
        for group_data in groups_data:
            group, created = PrivateGroup.objects.get_or_create(
                name=group_data['name'],
                defaults=group_data
            )
            
            if created:
                created_count += 1
                
                # Add random members
                admin = random.choice(users)
                GroupMembership.objects.create(
                    group=group,
                    user=admin,
                    role='owner',
                    status='active',
                    joined_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                
                # Add other members
                members_count = random.randint(5, 20)
                available_users = [u for u in users if u != admin]
                selected_members = random.sample(available_users, min(members_count, len(available_users)))
                
                for member in selected_members:
                    GroupMembership.objects.create(
                        group=group,
                        user=member,
                        role=random.choice(['member', 'moderator']),
                        status='active',
                        joined_at=timezone.now() - timedelta(days=random.randint(1, 30))
                    )
                
                # Update member count
                group.member_count = GroupMembership.objects.filter(group=group, status='active').count()
                group.save()

        return created_count

    def create_follows(self):
        """Create user follow relationships"""
        users = list(User.objects.filter(is_active=True))
        if len(users) < 2:
            return 0

        created_count = 0
        
        for user in users:
            # Each user follows 3-8 random other users
            follow_count = random.randint(3, min(8, len(users) - 1))
            potential_follows = [u for u in users if u != user]
            
            if not potential_follows:
                continue
                
            users_to_follow = random.sample(potential_follows, min(follow_count, len(potential_follows)))
            
            for followed_user in users_to_follow:
                follow, created = UserFollow.objects.get_or_create(
                    follower=user,
                    followed=followed_user,
                    defaults={
                        'created_at': timezone.now() - timedelta(days=random.randint(1, 90))
                    }
                )
                if created:
                    created_count += 1

        return created_count

    def create_posts(self):
        """Create sample posts and comments"""
        users = list(User.objects.filter(is_active=True))
        if not users:
            return 0

        post_contents = [
            "Que jogaço hoje! O futebol brasileiro está cada vez melhor! ⚽🇧🇷",
            "Análise tática do último jogo disponível no blog. Confiram! 📊",
            "Alguém mais acha que o VAR precisa ser mais rápido? 🤔",
            "Melhor contratação do ano? Deixem suas opiniões! 💭",
            "Estatísticas impressionantes do Brasileirão este ano! 📈",
            "Clássico domingo! Quem vocês acham que vai levar? 🏆",
            "Nosso time está evoluindo muito taticamente! 🎯",
            "Mercado da bola movimentado! Quais as próximas novidades? 💰",
            "Que saudade de ver os estádios lotados! 🏟️",
            "Temporada está sendo incrível! Muito equilíbrio! ⚽"
        ]

        posts_created = 0
        
        for _ in range(random.randint(20, 40)):
            user = random.choice(users)
            content = random.choice(post_contents)
            
            try:
                post = Post.objects.create(
                    author=user,
                    content=content,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    likes_count=random.randint(0, 100),
                    comments_count=random.randint(0, 20)
                )
                posts_created += 1
                
                # Add some comments
                comment_count = random.randint(0, 5)
                for _ in range(comment_count):
                    commenter = random.choice(users)
                    comment_text = random.choice([
                        "Concordo totalmente!",
                        "Ótima análise!",
                        "Pensamento interessante!",
                        "Não concordo, mas respeito a opinião",
                        "Excelente ponto de vista!",
                        "Muito bom!"
                    ])
                    
                    Comment.objects.create(
                        post=post,
                        author=commenter,
                        content=comment_text,
                        created_at=timezone.now() - timedelta(days=random.randint(0, 15))
                    )
                    
            except Exception as e:
                continue

        return posts_created
