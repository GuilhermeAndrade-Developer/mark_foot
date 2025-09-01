#!/usr/bin/env python3
"""
Seeder for API-related data (API usage logs, sync logs, etc.).
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
import json

# Add the project root to Python path
sys.path.append('/app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from api.models import ApiUsageLog, ApiSyncLog
from decimal import Decimal


def seed_api_logs():
    """Create sample API usage and sync logs"""
    
    print("🚀 Creating API logs data...")
    
    with transaction.atomic():
        # Get some users for API logs
        users = list(User.objects.all()[:10])
        if not users:
            print("❌ No users found. Please run user seeder first.")
            return
        
        # Create API Usage Logs
        print("📊 Creating API usage logs...")
        api_endpoints = [
            '/api/v1/teams/',
            '/api/v1/players/',
            '/api/v1/matches/',
            '/api/v1/predictions/',
            '/api/v1/statistics/',
            '/api/v1/competitions/',
            '/api/v1/user/profile/',
            '/api/v1/billing/invoices/',
            '/api/v1/ai/analysis/',
            '/api/v1/fantasy/leagues/'
        ]
        
        usage_logs_created = 0
        for _ in range(500):  # Create 500 API usage logs
            user = random.choice(users)
            endpoint = random.choice(api_endpoints)
            
            # Generate realistic timestamps (last 30 days)
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Generate response time (in milliseconds)
            response_time = random.randint(50, 2000)
            
            # Generate status codes (mostly successful)
            status_code = random.choices(
                [200, 201, 400, 401, 403, 404, 500],
                weights=[70, 10, 5, 5, 3, 5, 2]
            )[0]
            
            # Generate request data
            request_data = {
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'user_agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)',
                    'MarkFoot Mobile App/1.0.0',
                    'MarkFoot API Client/2.1.0'
                ]),
                'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'request_size': random.randint(100, 5000)
            }
            
            usage_log = ApiUsageLog.objects.create(
                user=user,
                endpoint=endpoint,
                timestamp=timestamp,
                response_time_ms=response_time,
                status_code=status_code,
                request_data=request_data
            )
            usage_logs_created += 1
        
        print(f"✅ Created {usage_logs_created} API usage logs")
        
        # Create API Sync Logs
        print("🔄 Creating API sync logs...")
        external_apis = [
            'football-api.com',
            'rapidapi-football',
            'api-sports.io',
            'openweathermap',
            'stripe-api',
            'mercadopago-api',
            'whatsapp-business-api'
        ]
        
        sync_logs_created = 0
        for _ in range(100):  # Create 100 sync logs
            api_name = random.choice(external_apis)
            
            # Generate sync timestamp (last 7 days)
            sync_timestamp = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Generate sync status (mostly successful)
            sync_status = random.choices(
                ['success', 'error', 'timeout', 'rate_limited'],
                weights=[75, 15, 5, 5]
            )[0]
            
            # Generate records processed
            records_processed = random.randint(0, 1000) if sync_status == 'success' else 0
            
            # Generate sync details
            sync_details = {
                'endpoint': f"https://{api_name}/v1/data",
                'duration_seconds': random.randint(1, 300),
                'data_type': random.choice(['teams', 'players', 'matches', 'statistics', 'odds']),
                'response_size_kb': random.randint(10, 5000)
            }
            
            if sync_status == 'error':
                sync_details['error_message'] = random.choice([
                    'Connection timeout',
                    'API key expired',
                    'Rate limit exceeded',
                    'Invalid response format',
                    'Server error 500'
                ])
            
            sync_log = ApiSyncLog.objects.create(
                api_name=api_name,
                sync_timestamp=sync_timestamp,
                sync_status=sync_status,
                records_processed=records_processed,
                sync_details=sync_details
            )
            sync_logs_created += 1
        
        print(f"✅ Created {sync_logs_created} API sync logs")
        
        print('\n🎉 API data seeded successfully!')
        
        # Display summary
        print(f'\n📊 API Data Summary:')
        print(f'   API Usage Logs: {ApiUsageLog.objects.count()}')
        print(f'   - Successful (2xx): {ApiUsageLog.objects.filter(status_code__gte=200, status_code__lt=300).count()}')
        print(f'   - Client Errors (4xx): {ApiUsageLog.objects.filter(status_code__gte=400, status_code__lt=500).count()}')
        print(f'   - Server Errors (5xx): {ApiUsageLog.objects.filter(status_code__gte=500).count()}')
        print(f'   API Sync Logs: {ApiSyncLog.objects.count()}')
        print(f'   - Successful Syncs: {ApiSyncLog.objects.filter(sync_status="success").count()}')
        print(f'   - Failed Syncs: {ApiSyncLog.objects.filter(sync_status="error").count()}')


if __name__ == '__main__':
    seed_api_logs()
