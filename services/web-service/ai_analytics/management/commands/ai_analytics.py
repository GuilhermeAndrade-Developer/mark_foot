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
                'test_basic',
                'test_all_services',
                'database_stats'
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
            elif action == 'test_all_services':
                self.test_all_services(options)
            elif action == 'database_stats':
                self.show_database_stats(options)
                
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
            analysis_date=timezone.now(),
            defaults={
                'sentiment': analysis['overall_sentiment'],
                'sentiment_score': analysis['sentiment_score'],
                'confidence': analysis.get('confidence', 0.8),
                'source_text': '; '.join(sample_texts),
                'source_platform': 'social_media',
                'keywords': analysis.get('keywords', [])
            }
        )
        
        self.stdout.write(f'🎯 Sentiment analysis for {player.name}:')
        self.stdout.write(f'   Overall Sentiment: {analysis["overall_sentiment"]}')
        self.stdout.write(f'   Sentiment Score: {analysis["sentiment_score"]:.2f}')
        self.stdout.write(f'   Status: {"Created" if created else "Updated"}')
    
    def test_all_services(self, options):
        """Test all AI services"""
        self.stdout.write('🧪 Testing All AI Services...')
        
        # Test sentiment analysis
        self.stdout.write('\n1️⃣ Testing Sentiment Analysis')
        self.analyze_sentiment({'limit': 2})
        
        # Show database stats
        self.stdout.write('\n2️⃣ Database Statistics')
        self.show_database_stats(options)
        
        self.stdout.write('\n✅ All tests completed!')
    
    def show_database_stats(self, options):
        """Show database statistics"""
        from ai_analytics.models import (
            SentimentAnalysis, InjuryPrediction, MarketValuePrediction,
            MatchPrediction, PlayerRecommendation, PlayStyleCluster,
            AnomalyDetection, TransferSimulation
        )
        
        self.stdout.write('📊 AI Analytics Database Statistics:')
        
        stats = {
            'Sentiment Analysis': SentimentAnalysis.objects.count(),
            'Injury Predictions': InjuryPrediction.objects.count(),
            'Market Value Predictions': MarketValuePrediction.objects.count(),
            'Match Predictions': MatchPrediction.objects.count(),
            'Player Recommendations': PlayerRecommendation.objects.count(),
            'Play Style Clusters': PlayStyleCluster.objects.count(),
            'Anomaly Detections': AnomalyDetection.objects.count(),
            'Transfer Simulations': TransferSimulation.objects.count(),
        }
        
        for name, count in stats.items():
            self.stdout.write(f'   {name}: {count}')
        
        total = sum(stats.values())
        self.stdout.write(f'\n📈 Total AI records: {total}')
