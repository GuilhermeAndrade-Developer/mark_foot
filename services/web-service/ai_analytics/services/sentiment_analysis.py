import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.utils import timezone

from core.models import Player, Team, Match, Competition
from ai_analytics.models import SentimentAnalysis
from .base_service import BaseAIService

logger = logging.getLogger(__name__)


class SentimentAnalysisService(BaseAIService):
    """Service for analyzing sentiment in social media and news about teams/players"""
    
    def __init__(self):
        super().__init__("sentiment_analysis", "1.0.0")
        self.sentiment_analyzer = None
        self.vader_analyzer = None
        self._initialize_analyzers()
        
    def _initialize_analyzers(self):
        """Initialize sentiment analysis tools"""
        try:
            # TextBlob for basic sentiment analysis
            from textblob import TextBlob
            self.sentiment_analyzer = TextBlob
            
            # VADER for social media sentiment
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            logger.info("Sentiment analyzers initialized successfully")
            
        except ImportError as e:
            logger.error(f"Error importing sentiment analysis libraries: {str(e)}")
    
    def analyze_text_sentiment(self, text: str, method: str = 'vader') -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            if method == 'vader' and self.vader_analyzer:
                return self._analyze_with_vader(cleaned_text)
            elif method == 'textblob' and self.sentiment_analyzer:
                return self._analyze_with_textblob(cleaned_text)
            else:
                # Fallback to simple keyword-based analysis
                return self._analyze_with_keywords(cleaned_text)
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags (but keep the content)
        text = re.sub(r'[@#]([A-Za-z0-9_]+)', r'\\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\\s+', ' ', text).strip()
        
        # Remove non-alphanumeric characters except common punctuation
        text = re.sub(r'[^a-zA-Z0-9\\s.,!?:;-]', '', text)
        
        return text
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # Determine overall sentiment
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'POSITIVE'
            elif compound <= -0.05:
                sentiment = 'NEGATIVE'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'sentiment': sentiment,
                'score': compound,
                'confidence': max(scores['pos'], scores['neu'], scores['neg']),
                'detailed_scores': {
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu'],
                    'compound': scores['compound']
                },
                'method': 'vader'
            }
            
        except Exception as e:
            logger.error(f"Error with VADER analysis: {str(e)}")
            return self._analyze_with_keywords(text)
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = self.sentiment_analyzer(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment
            if polarity > 0.1:
                sentiment = 'POSITIVE'
            elif polarity < -0.1:
                sentiment = 'NEGATIVE'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'sentiment': sentiment,
                'score': polarity,
                'confidence': 1 - subjectivity,  # Objective text = higher confidence
                'detailed_scores': {
                    'polarity': polarity,
                    'subjectivity': subjectivity
                },
                'method': 'textblob'
            }
            
        except Exception as e:
            logger.error(f"Error with TextBlob analysis: {str(e)}")
            return self._analyze_with_keywords(text)
    
    def _analyze_with_keywords(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based sentiment analysis"""
        try:
            # Portuguese and English sentiment keywords
            positive_keywords = [
                # English
                'excellent', 'amazing', 'fantastic', 'great', 'good', 'best', 'wonderful',
                'outstanding', 'brilliant', 'superb', 'impressive', 'incredible', 'perfect',
                'win', 'victory', 'champion', 'goal', 'score', 'success', 'talented',
                
                # Portuguese
                'excelente', 'incrível', 'fantástico', 'ótimo', 'bom', 'melhor', 'maravilhoso',
                'excepcional', 'brilhante', 'magnífico', 'impressionante', 'perfeito',
                'vitória', 'campeão', 'gol', 'sucesso', 'talentoso', 'craque', 'fenômeno'
            ]
            
            negative_keywords = [
                # English
                'terrible', 'awful', 'bad', 'worst', 'horrible', 'disappointing', 'poor',
                'failure', 'lose', 'defeat', 'miss', 'error', 'mistake', 'weak',
                
                # Portuguese
                'terrível', 'péssimo', 'ruim', 'pior', 'horrível', 'decepcionante', 'fraco',
                'falha', 'perder', 'derrota', 'erro', 'fraco', 'pipoca', 'vergonha'
            ]
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)
            
            # Calculate sentiment
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                sentiment = 'NEUTRAL'
                score = 0.0
                confidence = 0.3
            else:
                score = (positive_count - negative_count) / total_sentiment_words
                
                if score > 0.2:
                    sentiment = 'POSITIVE'
                elif score < -0.2:
                    sentiment = 'NEGATIVE'
                else:
                    sentiment = 'NEUTRAL'
                
                confidence = min(0.8, total_sentiment_words / 10)  # Max 80% confidence
            
            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': confidence,
                'detailed_scores': {
                    'positive_words': positive_count,
                    'negative_words': negative_count,
                    'total_words': len(text_lower.split())
                },
                'method': 'keywords'
            }
            
        except Exception as e:
            logger.error(f"Error with keyword analysis: {str(e)}")
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'error'
            }
    
    def extract_keywords(self, text: str, entity_type: str = None) -> List[str]:
        """Extract relevant keywords from text"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            words = cleaned_text.lower().split()
            
            # Common football/soccer keywords
            football_keywords = [
                'gol', 'goal', 'assist', 'assistência', 'vitória', 'victory', 'win',
                'derrota', 'defeat', 'loss', 'empate', 'draw', 'partida', 'match',
                'jogo', 'game', 'time', 'team', 'jogador', 'player', 'técnico', 'coach',
                'campeonato', 'championship', 'liga', 'league', 'copa', 'cup',
                'título', 'title', 'campeão', 'champion', 'rebaixamento', 'relegation'
            ]
            
            # Filter relevant keywords
            keywords = []
            for word in words:
                if (len(word) > 3 and  # Minimum length
                    word.isalpha() and  # Only letters
                    (word in football_keywords or  # Football-related
                     word.isupper() or  # Acronyms/names
                     word.istitle())):  # Proper nouns
                    keywords.append(word)
            
            # Remove duplicates and limit
            return list(dict.fromkeys(keywords))[:10]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def analyze_player_sentiment(self, player: Player, texts: List[str], source_platform: str = 'social_media') -> Dict[str, Any]:
        """Analyze sentiment for a specific player across multiple texts"""
        try:
            if not texts:
                return self._empty_sentiment_result()
            
            # Analyze each text
            all_results = []
            for text in texts:
                result = self.analyze_text_sentiment(text)
                result['text'] = text[:200]  # Store sample of original text
                all_results.append(result)
            
            # Aggregate results
            sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            total_score = 0
            total_confidence = 0
            all_keywords = []
            
            for result in all_results:
                sentiment_counts[result['sentiment']] += 1
                total_score += result['score']
                total_confidence += result['confidence']
                
                # Extract keywords from each text
                keywords = self.extract_keywords(result.get('text', ''), 'PLAYER')
                all_keywords.extend(keywords)
            
            # Calculate aggregated metrics
            num_texts = len(all_results)
            avg_score = total_score / num_texts
            avg_confidence = total_confidence / num_texts
            
            # Determine overall sentiment
            max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            
            # Save to database
            sentiment_analysis = SentimentAnalysis.objects.create(
                entity_type='PLAYER',
                entity_id=player.id,
                sentiment=max_sentiment,
                sentiment_score=avg_score,
                confidence=avg_confidence,
                source_text=f"Analyzed {num_texts} texts about {player.name}",
                source_platform=source_platform,
                keywords=list(dict.fromkeys(all_keywords))[:15],  # Top 15 unique keywords
                analysis_date=timezone.now()
            )
            
            return {
                'player_id': player.id,
                'player_name': player.name,
                'overall_sentiment': max_sentiment,
                'sentiment_score': avg_score,
                'confidence': avg_confidence,
                'text_count': num_texts,
                'sentiment_distribution': sentiment_counts,
                'keywords': list(dict.fromkeys(all_keywords))[:10],
                'individual_results': all_results,
                'analysis_id': sentiment_analysis.id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing player sentiment: {str(e)}")
            return self._empty_sentiment_result()
    
    def analyze_team_sentiment(self, team: Team, texts: List[str], source_platform: str = 'social_media') -> Dict[str, Any]:
        """Analyze sentiment for a specific team across multiple texts"""
        try:
            if not texts:
                return self._empty_sentiment_result()
            
            # Similar to player analysis but for teams
            all_results = []
            for text in texts:
                result = self.analyze_text_sentiment(text)
                result['text'] = text[:200]
                all_results.append(result)
            
            # Aggregate results
            sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            total_score = 0
            total_confidence = 0
            all_keywords = []
            
            for result in all_results:
                sentiment_counts[result['sentiment']] += 1
                total_score += result['score']
                total_confidence += result['confidence']
                
                keywords = self.extract_keywords(result.get('text', ''), 'TEAM')
                all_keywords.extend(keywords)
            
            num_texts = len(all_results)
            avg_score = total_score / num_texts
            avg_confidence = total_confidence / num_texts
            max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            
            # Save to database
            sentiment_analysis = SentimentAnalysis.objects.create(
                entity_type='TEAM',
                entity_id=team.id,
                sentiment=max_sentiment,
                sentiment_score=avg_score,
                confidence=avg_confidence,
                source_text=f"Analyzed {num_texts} texts about {team.name}",
                source_platform=source_platform,
                keywords=list(dict.fromkeys(all_keywords))[:15],
                analysis_date=timezone.now()
            )
            
            return {
                'team_id': team.id,
                'team_name': team.name,
                'overall_sentiment': max_sentiment,
                'sentiment_score': avg_score,
                'confidence': avg_confidence,
                'text_count': num_texts,
                'sentiment_distribution': sentiment_counts,
                'keywords': list(dict.fromkeys(all_keywords))[:10],
                'individual_results': all_results,
                'analysis_id': sentiment_analysis.id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing team sentiment: {str(e)}")
            return self._empty_sentiment_result()
    
    def analyze_match_sentiment(self, match: Match, texts: List[str], source_platform: str = 'social_media') -> Dict[str, Any]:
        """Analyze sentiment for a specific match"""
        try:
            if not texts:
                return self._empty_sentiment_result()
            
            all_results = []
            for text in texts:
                result = self.analyze_text_sentiment(text)
                result['text'] = text[:200]
                all_results.append(result)
            
            # Aggregate results
            sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            total_score = 0
            total_confidence = 0
            all_keywords = []
            
            for result in all_results:
                sentiment_counts[result['sentiment']] += 1
                total_score += result['score']
                total_confidence += result['confidence']
                
                keywords = self.extract_keywords(result.get('text', ''), 'MATCH')
                all_keywords.extend(keywords)
            
            num_texts = len(all_results)
            avg_score = total_score / num_texts
            avg_confidence = total_confidence / num_texts
            max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            
            # Save to database
            sentiment_analysis = SentimentAnalysis.objects.create(
                entity_type='MATCH',
                entity_id=match.id,
                sentiment=max_sentiment,
                sentiment_score=avg_score,
                confidence=avg_confidence,
                source_text=f"Analyzed {num_texts} texts about {match.home_team.name} vs {match.away_team.name}",
                source_platform=source_platform,
                keywords=list(dict.fromkeys(all_keywords))[:15],
                analysis_date=timezone.now()
            )
            
            return {
                'match_id': match.id,
                'match_description': f"{match.home_team.name} vs {match.away_team.name}",
                'overall_sentiment': max_sentiment,
                'sentiment_score': avg_score,
                'confidence': avg_confidence,
                'text_count': num_texts,
                'sentiment_distribution': sentiment_counts,
                'keywords': list(dict.fromkeys(all_keywords))[:10],
                'individual_results': all_results,
                'analysis_id': sentiment_analysis.id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing match sentiment: {str(e)}")
            return self._empty_sentiment_result()
    
    def get_sentiment_trends(self, entity_type: str, entity_id: int, days_back: int = 30) -> Dict[str, Any]:
        """Get sentiment trends over time for an entity"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days_back)
            
            sentiments = SentimentAnalysis.objects.filter(
                entity_type=entity_type,
                entity_id=entity_id,
                analysis_date__gte=cutoff_date
            ).order_by('analysis_date')
            
            if not sentiments.exists():
                return {'message': 'No sentiment data found for the specified period'}
            
            # Group by day
            daily_sentiments = {}
            for sentiment in sentiments:
                day = sentiment.analysis_date.date()
                if day not in daily_sentiments:
                    daily_sentiments[day] = []
                daily_sentiments[day].append(sentiment)
            
            # Calculate daily averages
            trend_data = []
            for day, day_sentiments in daily_sentiments.items():
                avg_score = sum(s.sentiment_score for s in day_sentiments) / len(day_sentiments)
                sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
                
                for s in day_sentiments:
                    sentiment_counts[s.sentiment] += 1
                
                trend_data.append({
                    'date': day.isoformat(),
                    'avg_score': avg_score,
                    'sentiment_counts': sentiment_counts,
                    'total_analyses': len(day_sentiments)
                })
            
            # Calculate overall trend
            scores = [d['avg_score'] for d in trend_data]
            overall_trend = 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
            
            return {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'period_days': days_back,
                'overall_trend': overall_trend,
                'daily_data': trend_data,
                'total_analyses': sentiments.count(),
                'avg_sentiment_score': sum(scores) / len(scores) if scores else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment trends: {str(e)}")
            return {'error': str(e)}
    
    def _empty_sentiment_result(self) -> Dict[str, Any]:
        """Return empty sentiment result"""
        return {
            'overall_sentiment': 'NEUTRAL',
            'sentiment_score': 0.0,
            'confidence': 0.0,
            'text_count': 0,
            'sentiment_distribution': {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0},
            'keywords': [],
            'individual_results': []
        }
    
    def simulate_social_media_data(self, entity_type: str, entity_id: int, num_texts: int = 10) -> List[str]:
        """Generate simulated social media texts for testing (in real implementation, this would fetch from APIs)"""
        try:
            # Sample texts for different entities (for demonstration)
            if entity_type == 'PLAYER':
                sample_texts = [
                    "What an incredible goal by this player! Absolutely brilliant!",
                    "Another disappointing performance, expected much better",
                    "This player is having an amazing season, definitely one of the best",
                    "Poor decision making in the final third, needs to improve",
                    "Fantastic assist! Great vision and technique",
                    "This player is past his prime, time to retire",
                    "Young talent with incredible potential for the future",
                    "Consistent performer, always delivers when needed",
                    "Injury prone player, can't stay fit for a full season",
                    "Outstanding work rate and dedication, true professional"
                ]
            elif entity_type == 'TEAM':
                sample_texts = [
                    "What a fantastic victory! The team played brilliantly today",
                    "Terrible performance, worst game of the season",
                    "This team has incredible potential this season",
                    "Poor tactics from the coach, need better strategy",
                    "Amazing teamwork and coordination on the field",
                    "Disappointing transfer window, needed better signings",
                    "Great defensive performance, solid at the back",
                    "Attack is lacking creativity, need more goals",
                    "Best team in the league right now, playing excellent football",
                    "Management needs to make changes, current approach not working"
                ]
            else:  # MATCH
                sample_texts = [
                    "What an exciting match! Both teams played their hearts out",
                    "Boring game, nothing happened for 90 minutes",
                    "Incredible comeback victory, never seen anything like it",
                    "Poor referee decisions ruined the match",
                    "Amazing goals and great entertainment for the fans",
                    "Disappointing result, expected much better from both teams",
                    "Fantastic atmosphere and passionate supporters",
                    "Too many cards and fouls, not good football",
                    "Perfect match for neutrals, end-to-end action",
                    "Controversial ending, will be talking about this for weeks"
                ]
            
            # Return a random selection
            import random
            return random.sample(sample_texts, min(num_texts, len(sample_texts)))
            
        except Exception as e:
            logger.error(f"Error generating sample texts: {str(e)}")
            return ["Sample text for sentiment analysis testing"]
