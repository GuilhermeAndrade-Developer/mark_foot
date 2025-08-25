import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.models import Match, Player, Team
from ai_analytics.models import SentimentAnalysis
from ai_analytics.services.sentiment_analysis import SentimentAnalysisService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'AI Analytics Command - Train models and generate predictions/recommendations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=[
                'analyze_sentiment',
                'test_basic'
            ],
            default='test_basic',
            help='Action to perform'
        )
        
        parser.add_argument(
            '--player-id',
            type=int,
            help='Specific player ID for analysis'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=3,
            help='Limit number of results'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        action = options['action']
        
        self.stdout.write(
            self.style.SUCCESS(f'🤖 Starting AI Analytics - Action: {action}')
        )
        
        try:
            if action == 'analyze_sentiment':
                self.analyze_sentiment(options)
            elif action == 'test_basic':
                self.test_basic_functionality(options)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            logger.error(f"AI Analytics command error: {str(e)}")
    
    def test_basic_functionality(self, options):
        """Test basic functionality"""
        self.stdout.write('🔧 Testing basic AI functionality...')
        
        # Test data availability
        players_count = Player.objects.count()
        teams_count = Team.objects.count()
        matches_count = Match.objects.count()
        
        self.stdout.write(f'📊 Data availability:')
        self.stdout.write(f'   Players: {players_count}')
        self.stdout.write(f'   Teams: {teams_count}')
        self.stdout.write(f'   Matches: {matches_count}')
        
        if players_count > 0:
            # Test sentiment analysis
            self.stdout.write('\n🧪 Testing sentiment analysis...')
            self.analyze_sentiment(options)
        else:
            self.stdout.write('⚠️  No players found for testing')
    
    def analyze_sentiment(self, options):
        """Analyze sentiment for players"""
        self.stdout.write('😊 Analyzing sentiment...')
        
        service = SentimentAnalysisService()
        
        # Analyze for specific player or all players
        player_id = options.get('player_id')
        limit = options.get('limit', 3)
        
        if player_id:
            try:
                player = Player.objects.get(id=player_id)
                self._analyze_single_player(service, player)
                
            except Player.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Player with ID {player_id} not found'))
        else:
            # Analyze sentiment for multiple players
            players = Player.objects.all()[:limit]
            analyses_count = 0
            
            for player in players:
                try:
                    self._analyze_single_player(service, player)
                    analyses_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️  Error analyzing {player.name}: {str(e)}'))
                    logger.warning(f"Error analyzing sentiment for {player.name}: {str(e)}")
            
            self.stdout.write(f'✅ Generated {analyses_count} sentiment analyses')
    
    def _analyze_single_player(self, service, player):
        """Analyze sentiment for a single player"""
        # Generate sample texts for sentiment analysis
        sample_texts = [
            f"Great performance by {player.name} in the last match!",
            f"{player.name} is showing excellent form this season.",
            f"Fans are excited about {player.name}'s recent improvements.",
            f"{player.name} scored a brilliant goal yesterday!",
            f"The team looks much better with {player.name} on the field."
        ]
        
        analysis = service.analyze_player_sentiment(player, sample_texts)
        
        # Save sentiment analysis
        sentiment_obj, created = SentimentAnalysis.objects.update_or_create(
            entity_type='PLAYER',
            entity_id=player.id,
            analysis_date=timezone.now().date(),
            defaults={
                'sentiment': analysis['overall_sentiment'],
                'sentiment_score': analysis['sentiment_score'],
                'analysis_details': analysis,
                'source_platform': 'social_media',
                'model_version': 'v1.0'
            }
        )
        
        self.stdout.write(f'🎯 Sentiment analysis for {player.name}:')
        self.stdout.write(f'   Overall Sentiment: {analysis["overall_sentiment"]}')
        self.stdout.write(f'   Sentiment Score: {analysis["sentiment_score"]:.2f}')
        self.stdout.write(f'   Status: {"Created" if created else "Updated"}')
