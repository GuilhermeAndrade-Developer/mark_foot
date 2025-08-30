"""
Management command to set up social features with sample data.
"""
import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from social.models import (
    SocialPlatform, ShareTemplate, PrivateGroup, GroupMembership
)


class Command(BaseCommand):
    help = 'Setup social features with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all social data before creating new',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting social data...')
            self.reset_data()

        self.stdout.write('Creating social platforms...')
        self.create_platforms()
        
        self.stdout.write('Creating share templates...')
        self.create_templates()
        
        self.stdout.write('Creating sample groups...')
        self.create_groups()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up social features!')
        )

    def reset_data(self):
        """Reset all social data"""
        SocialPlatform.objects.all().delete()
        ShareTemplate.objects.all().delete()
        PrivateGroup.objects.all().delete()

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
                'base_url': 'https://twitter.com'
            },
            {
                'name': 'instagram',
                'display_name': 'Instagram',
                'character_limit': 2200,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://instagram.com'
            },
            {
                'name': 'tiktok',
                'display_name': 'TikTok',
                'character_limit': 2200,
                'supports_images': False,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://tiktok.com'
            },
            {
                'name': 'facebook',
                'display_name': 'Facebook',
                'character_limit': 63206,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://facebook.com'
            },
            {
                'name': 'linkedin',
                'display_name': 'LinkedIn',
                'character_limit': 3000,
                'supports_images': True,
                'supports_videos': True,
                'supports_hashtags': True,
                'base_url': 'https://linkedin.com'
            }
        ]

        for platform_data in platforms_data:
            platform, created = SocialPlatform.objects.get_or_create(
                name=platform_data['name'],
                defaults=platform_data
            )
            if created:
                self.stdout.write(f'  ✓ Created platform: {platform.display_name}')
            else:
                self.stdout.write(f'  - Platform already exists: {platform.display_name}')

    def create_templates(self):
        """Create share templates"""
        templates_data = [
            # Twitter templates
            {
                'platform_name': 'twitter',
                'name': 'Match Result - Twitter',
                'template_type': 'match_result',
                'title_template': '🔥 {home_team} vs {away_team}',
                'content_template': '⚽ FINAL: {home_team} {home_score} - {away_score} {away_team}\n\n{match_summary}\n\n#Football #MarkFoot #{home_team_slug} #{away_team_slug}',
                'hashtags': '#Football #MarkFoot #MatchResult',
                'available_variables': ['home_team', 'away_team', 'home_score', 'away_score', 'match_summary', 'home_team_slug', 'away_team_slug']
            },
            {
                'platform_name': 'twitter',
                'name': 'Player Stats - Twitter',
                'template_type': 'player_stat',
                'title_template': '⭐ {player_name} Performance',
                'content_template': '🌟 {player_name} está em grande forma!\n\n📊 Stats hoje:\n⚽ {goals} gols\n🎯 {assists} assistências\n💯 {rating}/10 rating\n\n#Football #MarkFoot #{team_slug} #{player_slug}',
                'hashtags': '#Football #MarkFoot #PlayerStats',
                'available_variables': ['player_name', 'goals', 'assists', 'rating', 'team_slug', 'player_slug']
            },
            
            # Instagram templates
            {
                'platform_name': 'instagram',
                'name': 'Match Result - Instagram',
                'template_type': 'match_result',
                'title_template': '🔥 {home_team} vs {away_team} - FINAL',
                'content_template': '⚽ QUE JOGO! {home_team} {home_score} - {away_score} {away_team}\n\n{match_summary}\n\n🏆 {competition_name}\n📅 {match_date}\n🏟️ {stadium}\n\nO que acharam do resultado? 👇\n\n#Football #MarkFoot #{home_team_slug} #{away_team_slug} #MatchResult #Soccer',
                'hashtags': '#Football #MarkFoot #MatchResult #Soccer',
                'available_variables': ['home_team', 'away_team', 'home_score', 'away_score', 'match_summary', 'competition_name', 'match_date', 'stadium', 'home_team_slug', 'away_team_slug']
            },
            
            # TikTok templates
            {
                'platform_name': 'tiktok',
                'name': 'Goal Highlights - TikTok',
                'template_type': 'match_result',
                'title_template': '🔥 GOLAÇO!',
                'content_template': '⚽ GOLAÇO de {player_name}! 🔥\n\n{home_team} vs {away_team}\nMinuto {goal_minute}\n\nQue jogada incrível! 🤩\n\nSigam para mais highlights! ⚽\n\n#Football #Goal #Soccer #MarkFoot #{team_slug} #Highlight #Amazing #Futebol',
                'hashtags': '#Football #Goal #Soccer #MarkFoot #Highlight',
                'available_variables': ['player_name', 'home_team', 'away_team', 'goal_minute', 'team_slug']
            }
        ]

        for template_data in templates_data:
            platform = SocialPlatform.objects.get(name=template_data['platform_name'])
            template_data_clean = {k: v for k, v in template_data.items() if k != 'platform_name'}
            template_data_clean['platform'] = platform
            
            template, created = ShareTemplate.objects.get_or_create(
                name=template_data['name'],
                platform=platform,
                defaults=template_data_clean
            )
            if created:
                self.stdout.write(f'  ✓ Created template: {template.name}')
            else:
                self.stdout.write(f'  - Template already exists: {template.name}')

    def create_groups(self):
        """Create sample private groups"""
        groups_data = [
            {
                'name': 'Família Santos FC',
                'description': 'Grupo da família para discutir os jogos do Santos',
                'group_type': 'family',
                'privacy_level': 'private',
                'max_members': 20,
                'allow_member_invites': True,
                'require_admin_approval': False
            },
            {
                'name': 'Amigos do Futebol',
                'description': 'Grupo de amigos para falar sobre futebol em geral',
                'group_type': 'friends',
                'privacy_level': 'restricted',
                'max_members': 50,
                'allow_member_invites': True,
                'require_admin_approval': True
            },
            {
                'name': 'Torcedores do Palmeiras',
                'description': 'Grupo público para torcedores do Palmeiras',
                'group_type': 'team_fans',
                'privacy_level': 'public',
                'max_members': 1000,
                'allow_member_invites': True,
                'require_admin_approval': False
            },
            {
                'name': 'Champions League 2024',
                'description': 'Discussões sobre a Champions League',
                'group_type': 'competition',
                'privacy_level': 'public',
                'max_members': 500,
                'allow_member_invites': True,
                'require_admin_approval': False
            },
            {
                'name': 'Analistas Táticos',
                'description': 'Grupo para análises táticas profundas',
                'group_type': 'custom',
                'privacy_level': 'restricted',
                'max_members': 100,
                'allow_member_invites': False,
                'require_admin_approval': True
            }
        ]

        for group_data in groups_data:
            group, created = PrivateGroup.objects.get_or_create(
                name=group_data['name'],
                defaults=group_data
            )
            if created:
                self.stdout.write(f'  ✓ Created group: {group.name}')
                
                # Create admin membership for superuser
                try:
                    admin_user = User.objects.filter(is_superuser=True).first()
                    if admin_user:
                        GroupMembership.objects.create(
                            group=group,
                            user=admin_user,
                            role='owner',
                            status='active'
                        )
                        group.member_count = 1
                        group.save(update_fields=['member_count'])
                        self.stdout.write(f'    ✓ Added {admin_user.username} as owner')
                except Exception as e:
                    self.stdout.write(f'    - Could not add admin: {e}')
            else:
                self.stdout.write(f'  - Group already exists: {group.name}')

        self.stdout.write('\n📊 Social Features Summary:')
        self.stdout.write(f'  • Platforms: {SocialPlatform.objects.count()}')
        self.stdout.write(f'  • Templates: {ShareTemplate.objects.count()}')
        self.stdout.write(f'  • Groups: {PrivateGroup.objects.count()}')
        self.stdout.write(f'  • Memberships: {GroupMembership.objects.count()}')
