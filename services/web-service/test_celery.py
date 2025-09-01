#!/usr/bin/env python
import os
import django
import sys

# Add the current directory to Python path
sys.path.append('/app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from core.tasks import monitor_live_matches
from celery import current_app
from django.core.cache import cache

print('=== ENVIRONMENT ===')
print(f'REDIS_URL: {os.getenv("REDIS_URL", "Not set")}')

print('\n=== CELERY CONFIGURATION ===')
print(f'Broker URL: {current_app.conf.broker_url}')
print(f'Result Backend: {current_app.conf.result_backend}')

print('\n=== TESTING REDIS CONNECTION ===')
try:
    # Test Redis connection via Django cache
    cache.set('test_key', 'test_value', 10)
    result = cache.get('test_key')
    print(f'Redis connection: {"OK" if result == "test_value" else "Failed"}')
    if result == "test_value":
        cache.delete('test_key')
except Exception as e:
    print(f'Redis error: {e}')

print('\n=== TESTING CELERY TASK ===')
try:
    # Test task creation (not execution)
    task_signature = monitor_live_matches.s()
    print(f'Task signature created: {task_signature}')
    print('Task definition: OK')
except Exception as e:
    print(f'Task error: {e}')

print('\n=== CELERY WORKER STATUS ===')
try:
    # Check if workers are available
    inspect = current_app.control.inspect()
    active_workers = inspect.active()
    if active_workers:
        print(f'Active workers: {list(active_workers.keys())}')
    else:
        print('No active workers found')
except Exception as e:
    print(f'Worker check error: {e}')

print('\n=== TEST COMPLETED ===')
