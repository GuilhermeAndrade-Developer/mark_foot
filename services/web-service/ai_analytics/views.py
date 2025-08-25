from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.utils.decorators import method_decorator
from django.views import View
import json

from .models import (
    SentimentAnalysis, InjuryPrediction, MarketValuePrediction,
    MatchPrediction, PlayerRecommendation, PlayStyleCluster,
    AnomalyDetection, TransferSimulation
)


def ai_stats(request):
    """Return AI analytics statistics"""
    stats = {
        'sentiment_analysis': SentimentAnalysis.objects.count(),
        'injury_predictions': InjuryPrediction.objects.count(),
        'market_value_predictions': MarketValuePrediction.objects.count(),
        'match_predictions': MatchPrediction.objects.count(),
        'player_recommendations': PlayerRecommendation.objects.count(),
        'play_style_clusters': PlayStyleCluster.objects.count(),
        'anomaly_detections': AnomalyDetection.objects.count(),
        'transfer_simulations': TransferSimulation.objects.count(),
    }
    
    stats['total_records'] = sum(stats.values())
    
    return JsonResponse({
        'status': 'success',
        'data': stats,
        'message': 'AI Analytics statistics retrieved successfully'
    })


def sentiment_analysis_list(request):
    """Return sentiment analysis results"""
    limit = int(request.GET.get('limit', 10))
    
    sentiments = SentimentAnalysis.objects.select_related().order_by('-created_at')[:limit]
    
    data = []
    for sentiment in sentiments:
        data.append({
            'id': sentiment.id,
            'entity_type': sentiment.entity_type,
            'entity_id': sentiment.entity_id,
            'sentiment': sentiment.sentiment,
            'sentiment_score': sentiment.sentiment_score,
            'confidence': sentiment.confidence,
            'source_platform': sentiment.source_platform,
            'analysis_date': sentiment.analysis_date.isoformat(),
            'created_at': sentiment.created_at.isoformat(),
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data,
        'count': len(data),
        'message': f'Retrieved {len(data)} sentiment analyses'
    })


@csrf_exempt
def test_ai_services(request):
    """Test AI services endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            action = data.get('action', 'test_basic')
            limit = data.get('limit', 3)
            
            # Call the management command
            call_command('ai_analytics', action=action, limit=limit)
            
            return JsonResponse({
                'status': 'success',
                'message': f'AI test "{action}" executed successfully',
                'action': action,
                'limit': limit
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error executing AI test: {str(e)}'
            }, status=500)
    
    else:
        # GET request - return available actions
        return JsonResponse({
            'status': 'success',
            'available_actions': [
                'analyze_sentiment',
                'test_basic',
                'test_all_services',
                'database_stats'
            ],
            'message': 'POST to this endpoint with {"action": "test_basic", "limit": 3} to run tests'
        })
