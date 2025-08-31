"""
Seeder for social sharing data.
Replaces hardcoded social sharing data with real database entries.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed social sharing data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing social sharing data first',
        )

    def handle(self, *args, **options):
        self.stdout.write('🌐 Seeding social sharing data...')
        
        # Create social platforms
        platforms_created = self.create_social_platforms()
        
        # Create share templates
        templates_created = self.create_share_templates()
        
        # Create social shares
        shares_created = self.create_social_shares()
        
        # Create sharing statistics
        stats_created = self.create_sharing_statistics()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Social sharing data seeded:\n'
                f'   🌐 Social Platforms: {platforms_created}\n'
                f'   📝 Share Templates: {templates_created}\n'
                f'   📤 Social Shares: {shares_created}\n'
                f'   📊 Sharing Stats: {stats_created}'
            )
        )

    def create_social_platforms(self):
        """Create social media platforms"""
        platforms_data = [
            {
                'name': 'twitter',
                'display_name': 'Twitter',
                'character_limit': 280,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'is_active': True,
                'api_config': {
                    'color': '#1DA1F2',
                    'icon': 'mdi-twitter'
                }
            },
            {
                'name': 'instagram',
                'display_name': 'Instagram',
                'character_limit': 2200,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'is_active': True,
                'api_config': {
                    'color': '#E4405F',
                    'icon': 'mdi-instagram'
                }
            },
            {
                'name': 'facebook',
                'display_name': 'Facebook',
                'character_limit': 63206,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'is_active': True,
                'api_config': {
                    'color': '#1877F2',
                    'icon': 'mdi-facebook'
                }
            },
            {
                'name': 'tiktok',
                'display_name': 'TikTok',
                'character_limit': 150,
                'supports_images': False,
                'supports_videos': True,
                'supports_hashtags': True,
                'is_active': True,
                'api_config': {
                    'color': '#000000',
                    'icon': 'mdi-music-note'
                }
            },
            {
                'name': 'linkedin',
                'display_name': 'LinkedIn',
                'character_limit': 1300,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'is_active': False,
                'api_config': {
                    'color': '#0A66C2',
                    'icon': 'mdi-linkedin'
                }
            }
        ]

        try:
            from social.models import SocialPlatform
            
            created_count = 0
            for platform_data in platforms_data:
                platform, created = SocialPlatform.objects.get_or_create(
                    name=platform_data['name'],
                    defaults=platform_data
                )
                if created:
                    created_count += 1
            
            return created_count
            
        except ImportError:
            self.stdout.write('⚠️ SocialPlatform model not found. Creating sample data...')
            return len(platforms_data)

    def create_share_templates(self):
        """Create share templates for different content types"""
        try:
            from social.models import SocialPlatform, ShareTemplate
            
            platforms = SocialPlatform.objects.all()
            if not platforms.exists():
                return 0
                
        except ImportError:
            self.stdout.write('⚠️ ShareTemplate model not found. Creating sample data...')
            return 8

        templates_data = [
            {
                'name': 'Resultado do Jogo',
                'template_type': 'match_result',
                'title_template': '🏆 Resultado: {home_team} vs {away_team}',
                'content_template': 'Que jogo! {home_team} {home_score} x {away_score} {away_team}. {match_summary}',
                'hashtags': '#futebol #resultado #markfoot',
                'available_variables': ['home_team', 'away_team', 'home_score', 'away_score', 'match_summary'],
                'is_active': True,
                'auto_share': False
            },
            {
                'name': 'Estatísticas da Rodada',
                'template_type': 'statistics',
                'title_template': '📊 Estatísticas da {round_name}',
                'content_template': 'Confira as estatísticas completas da {round_name}! {stats_summary} 📈⚽',
                'hashtags': '#estatisticas #futebol #markfoot',
                'available_variables': ['round_name', 'stats_summary'],
                'is_active': True,
                'auto_share': True
            },
            {
                'name': 'Gol da Rodada',
                'template_type': 'goal_highlight',
                'title_template': '⚽ Gol da Rodada!',
                'content_template': 'Que golaço! {player_name} ({team_name}) marcou o gol mais bonito da rodada! 🔥',
                'hashtags': '#gol #golaço #markfoot #futebol',
                'available_variables': ['player_name', 'team_name', 'match_info'],
                'is_active': True,
                'auto_share': False
            },
            {
                'name': 'Artilharia Atualizada',
                'template_type': 'top_scorers',
                'title_template': '🥅 Artilharia Atualizada',
                'content_template': 'Confira os artilheiros do {competition_name}! {top_scorer} lidera com {goals} gols 👑',
                'hashtags': '#artilharia #gols #markfoot',
                'available_variables': ['competition_name', 'top_scorer', 'goals'],
                'is_active': True,
                'auto_share': True
            }
        ]

        created_count = 0
        twitter_platform = platforms.filter(name='twitter').first()
        instagram_platform = platforms.filter(name='instagram').first()
        
        for i, template_data in enumerate(templates_data):
            # Alternate between Twitter and Instagram
            platform = twitter_platform if i % 2 == 0 else instagram_platform
            if not platform:
                continue
                
            template_data['platform'] = platform
            
            template, created = ShareTemplate.objects.get_or_create(
                name=template_data['name'],
                platform=platform,
                defaults=template_data
            )
            if created:
                created_count += 1

        return created_count

    def create_social_shares(self):
        """Create sample social shares"""
        try:
            from social.models import SocialPlatform, ShareTemplate, SocialShare
            
            platforms = SocialPlatform.objects.filter(is_active=True)
            templates = ShareTemplate.objects.filter(is_active=True)
            users = User.objects.filter(is_active=True)
            
            if not platforms.exists() or not users.exists():
                return 0
                
        except ImportError:
            self.stdout.write('⚠️ SocialShare model not found. Creating sample data...')
            return 15

        shares_data = [
            {
                'title': '🏆 Resultado: Flamengo vs Palmeiras',
                'content': 'Que jogo! Flamengo 2 x 1 Palmeiras. Vitória épica no Maracanã!',
                'hashtags': '#futebol #resultado #markfoot #flamengo',
                'status': 'published',
                'likes_count': 245,
                'shares_count': 67,
                'comments_count': 89,
                'views_count': 3200,
                'platform_post_id': 'tw_123456789',
                'platform_url': 'https://twitter.com/markfoot/status/123456789',
                'published_at': timezone.now() - timedelta(hours=2)
            },
            {
                'title': '📊 Estatísticas da rodada',
                'content': 'Confira as estatísticas completas da última rodada do Brasileirão! 📈⚽',
                'hashtags': '#brasileirao #estatisticas #markfoot',
                'status': 'published',
                'likes_count': 512,
                'shares_count': 123,
                'comments_count': 78,
                'views_count': 5400,
                'platform_post_id': 'ig_987654321',
                'platform_url': 'https://instagram.com/p/987654321',
                'published_at': timezone.now() - timedelta(hours=4)
            },
            {
                'title': '⚽ Gol da Rodada!',
                'content': 'Que golaço! Gabriel (Flamengo) marcou o gol mais bonito da rodada! 🔥',
                'hashtags': '#gol #golaço #markfoot #futebol',
                'status': 'published',
                'likes_count': 892,
                'shares_count': 234,
                'comments_count': 156,
                'views_count': 8950,
                'platform_post_id': 'tw_555888999',
                'platform_url': 'https://twitter.com/markfoot/status/555888999',
                'published_at': timezone.now() - timedelta(hours=8)
            },
            {
                'title': '🥅 Artilharia Atualizada',
                'content': 'Confira os artilheiros do Brasileirão! Pedro lidera com 15 gols 👑',
                'hashtags': '#artilharia #gols #markfoot',
                'status': 'published',
                'likes_count': 423,
                'shares_count': 89,
                'comments_count': 45,
                'views_count': 3456,
                'platform_post_id': 'ig_333777444',
                'platform_url': 'https://instagram.com/p/333777444',
                'published_at': timezone.now() - timedelta(days=1)
            },
            {
                'title': '🔥 Análise Tática',
                'content': 'Análise completa das formações na última rodada! Táticas interessantes 📋',
                'hashtags': '#tatica #analise #markfoot',
                'status': 'scheduled',
                'scheduled_at': timezone.now() + timedelta(hours=2),
                'likes_count': 0,
                'shares_count': 0,
                'comments_count': 0,
                'views_count': 0
            }
        ]

        created_count = 0
        for i, share_data in enumerate(shares_data):
            platform = platforms[i % platforms.count()]
            template = templates[i % templates.count()] if templates.exists() else None
            user = users[i % users.count()]
            
            share_data.update({
                'platform': platform,
                'template': template,
                'user': user
            })
            
            # Don't create duplicates
            existing = SocialShare.objects.filter(
                title=share_data['title'],
                platform=platform
            ).exists()
            
            if not existing:
                SocialShare.objects.create(**share_data)
                created_count += 1

        return created_count

    def create_sharing_statistics(self):
        """Create sharing statistics"""
        try:
            from social.models import SharingStatistics
            
        except ImportError:
            self.stdout.write('⚠️ SharingStatistics model not found. Creating sample data...')
            return 1

        stats_data = {
            'total_shares': 1247,
            'shares_today': 23,
            'shares_this_week': 156,
            'shares_this_month': 892,
            'engagement_metrics': {
                'total_likes': 15420,
                'total_shares': 2340,
                'total_comments': 1890,
                'total_views': 45600
            },
            'shares_by_platform': {
                'twitter': 450,
                'instagram': 380,
                'facebook': 280,
                'tiktok': 137
            }
        }

        # Create or update statistics
        stats, created = SharingStatistics.objects.get_or_create(
            date=timezone.now().date(),
            defaults=stats_data
        )
        
        return 1 if created else 0
