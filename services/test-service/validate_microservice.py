#!/usr/bin/env python3
"""
Quick validation script for the test service microservice
"""

import os
import sys
import subprocess
from pathlib import Path

def check_structure():
    """Check if all required files and directories exist"""
    base_path = Path(__file__).parent
    
    required_items = [
        'Dockerfile',
        'requirements.txt',
        'pytest.ini',
        'test_settings.py',
        'run_tests.sh',
        'run_tests.ps1',
        'Makefile',
        'docker-compose.test.yml',
        'auth/',
        'data/', 
        'integration/',
        'unit/',
        'test_apps/'
    ]
    
    print("🔍 Checking test service structure...")
    
    missing = []
    for item in required_items:
        path = base_path / item
        if not path.exists():
            missing.append(item)
        else:
            print(f"✅ {item}")
    
    if missing:
        print(f"\n❌ Missing items: {missing}")
        return False
    
    print("\n✅ All required files and directories are present!")
    return True

def check_test_apps():
    """Check test apps structure"""
    print("\n🔍 Checking test apps...")
    
    apps_path = Path(__file__).parent / 'test_apps'
    expected_apps = [
        'core', 'api', 'gamification', 'social', 'forum', 
        'chat', 'content', 'polls', 'data_management', 
        'ai_analytics', 'api_integration'
    ]
    
    for app in expected_apps:
        app_path = apps_path / app
        if app_path.exists() and (app_path / '__init__.py').exists():
            print(f"✅ test_apps.{app}")
        else:
            print(f"❌ test_apps.{app}")

def validate_docker_files():
    """Validate Docker related files"""
    print("\n🔍 Validating Docker files...")
    
    dockerfile = Path(__file__).parent / 'Dockerfile'
    compose_file = Path(__file__).parent / 'docker-compose.test.yml'
    
    if dockerfile.exists():
        print("✅ Dockerfile exists")
        with open(dockerfile) as f:
            content = f.read()
            if 'FROM python:3.11-slim' in content:
                print("✅ Dockerfile uses Python 3.11")
            if 'pytest' in content:
                print("✅ Dockerfile includes pytest")
    
    if compose_file.exists():
        print("✅ Docker Compose file exists")

def main():
    """Main validation function"""
    print("🧪 Mark Foot Test Service Validation")
    print("=" * 40)
    
    # Check basic structure
    if not check_structure():
        sys.exit(1)
    
    # Check test apps
    check_test_apps()
    
    # Validate Docker files
    validate_docker_files()
    
    print("\n" + "=" * 40)
    print("🎉 Test Service Microservice is ready!")
    print("\nNext steps:")
    print("1. Build the container: make build")
    print("2. Run tests: make test")
    print("3. Or use Docker Compose with --profile testing")
    print("\n📖 See README_TEST_SERVICE.md for detailed instructions")

if __name__ == "__main__":
    main()
