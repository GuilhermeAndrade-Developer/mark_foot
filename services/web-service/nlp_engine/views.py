from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Intent, EntityType, TrainingPhrase, UserQuery
from .services import FootballNLPService, ResponseGenerator
from .serializers import (
    IntentSerializer, EntityTypeSerializer, TrainingPhraseSerializer,
    UserQuerySerializer, QueryRequestSerializer, QueryResponseSerializer
)


class ProcessQueryView(APIView):
    """
    API endpoint to process natural language queries
    """
    
    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        if serializer.is_valid():
            query_text = serializer.validated_data['query']
            user_phone = serializer.validated_data.get('user_phone')
            user_id = serializer.validated_data.get('user_id')
            
            # Process query with NLP service
            nlp_service = FootballNLPService()
            result = nlp_service.process_query(query_text, user_phone, user_id)
            
            # Generate response
            response_generator = ResponseGenerator()
            response_text = response_generator.generate_response(result, user_phone)
            
            # Prepare response data
            response_data = {
                'query': query_text,
                'intent': result['intent'],
                'intent_confidence': result['intent_confidence'],
                'entities': result['entities'],
                'response': response_text,
                'processing_time_ms': result['processing_time_ms'],
                'success': result['success']
            }
            
            response_serializer = QueryResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IntentListView(generics.ListCreateAPIView):
    """
    List and create intents
    """
    queryset = Intent.objects.filter(is_active=True)
    serializer_class = IntentSerializer


class EntityTypeListView(generics.ListCreateAPIView):
    """
    List and create entity types
    """
    queryset = EntityType.objects.filter(is_active=True)
    serializer_class = EntityTypeSerializer


class TrainingPhraseListView(generics.ListCreateAPIView):
    """
    List and create training phrases
    """
    queryset = TrainingPhrase.objects.filter(is_active=True)
    serializer_class = TrainingPhraseSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        intent = self.request.query_params.get('intent')
        if intent:
            queryset = queryset.filter(intent__name=intent)
        return queryset


class QueryAnalyticsView(APIView):
    """
    Analytics endpoint for query processing
    """
    
    def get(self, request):
        # Get date range (default: last 7 days)
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Basic query stats
        total_queries = UserQuery.objects.filter(timestamp__gte=start_date).count()
        successful_queries = UserQuery.objects.filter(
            timestamp__gte=start_date, 
            was_successful=True
        ).count()
        
        # Intent distribution
        intent_stats = UserQuery.objects.filter(
            timestamp__gte=start_date,
            was_successful=True
        ).values('detected_intent').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average processing time
        avg_processing_time = UserQuery.objects.filter(
            timestamp__gte=start_date,
            processing_time_ms__isnull=False
        ).aggregate(avg_time=Avg('processing_time_ms'))
        
        # Most common entities
        entity_stats = {}
        queries_with_entities = UserQuery.objects.filter(
            timestamp__gte=start_date,
            was_successful=True,
            detected_entities__isnull=False
        )
        
        for query in queries_with_entities:
            for entity_type, entities in query.detected_entities.items():
                if entity_type not in entity_stats:
                    entity_stats[entity_type] = 0
                entity_stats[entity_type] += len(entities)
        
        analytics_data = {
            'period_days': days,
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'success_rate': round((successful_queries / total_queries * 100), 2) if total_queries > 0 else 0,
            'average_processing_time_ms': round(avg_processing_time['avg_time'] or 0, 2),
            'intent_distribution': list(intent_stats),
            'entity_distribution': entity_stats,
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(analytics_data, status=status.HTTP_200_OK)
