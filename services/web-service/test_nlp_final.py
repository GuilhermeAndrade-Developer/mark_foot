#!/usr/bin/env python
"""
Teste final do NLP Engine
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from nlp_engine.models import UserQuery
from nlp_engine.services import FootballNLPService, ResponseGenerator
from django.db.models import Count

def test_nlp_engine():
    print('🧠 TESTE FINAL DO NLP ENGINE')
    print('=' * 50)

    # Verificar dados carregados
    print(f'Total de queries processadas: {UserQuery.objects.count()}')

    # Criar instâncias dos serviços
    nlp = FootballNLPService()
    response_gen = ResponseGenerator()

    # Testes com diferentes tipos de consulta
    test_queries = [
        'Como está o Flamengo?',
        'Estatísticas do Gabigol',
        'Tabela do Brasileirão',
        'Quero ser premium',
        'Quando joga o Palmeiras?'
    ]

    print('\n📝 TESTANDO QUERIES:')
    print('-' * 30)

    for i, query in enumerate(test_queries, 1):
        print(f'\n{i}. Query: "{query}"')
        
        try:
            # Processar com NLP
            result = nlp.process_query(query, user_phone='+5511999999999')
            
            # Gerar resposta
            response = response_gen.generate_response(result, user_phone='+5511999999999')
            
            print(f'   Intent: {result["intent"]} (confidence: {result["intent_confidence"]:.2f})')
            print(f'   Entities: {len(result["entities"])} tipos encontrados')
            
            # Mostrar entidades encontradas
            for entity_type, entities in result["entities"].items():
                print(f'     - {entity_type}: {len(entities)} itens')
                for entity in entities:
                    print(f'       * {entity["name"]} (conf: {entity["confidence"]:.2f})')
            
            print(f'   Response: {response[:100]}...')
            print(f'   ✅ Processado em {result["processing_time_ms"]}ms')
            
        except Exception as e:
            print(f'   ❌ Erro: {e}')
            import traceback
            traceback.print_exc()

    print('\n📊 ESTATÍSTICAS FINAIS:')
    print('-' * 30)

    # Estatísticas das queries
    total_queries = UserQuery.objects.count()
    successful_queries = UserQuery.objects.filter(was_successful=True).count()
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0

    print(f'Total de queries: {total_queries}')
    print(f'Queries bem-sucedidas: {successful_queries}')
    print(f'Taxa de sucesso: {success_rate:.1f}%')

    # Intents mais comuns
    intent_stats = UserQuery.objects.values('detected_intent').annotate(count=Count('id')).order_by('-count')[:5]

    print(f'\nIntents mais detectados:')
    for stat in intent_stats:
        print(f'  - {stat["detected_intent"]}: {stat["count"]} vezes')

    print('\n🎉 TESTE CONCLUÍDO COM SUCESSO!')

if __name__ == "__main__":
    test_nlp_engine()
