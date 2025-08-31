#!/usr/bin/env python
"""
Test runner script for Mark Foot project.
Validates that all test files are accessible and properly organized.
"""

import os
import sys
from pathlib import Path

def validate_test_structure():
    """Validate the test directory structure"""
    test_dir = Path(__file__).parent
    
    print("🔍 Validating test structure...")
    
    # Expected directories
    expected_dirs = [
        'auth',
        'data', 
        'integration',
        'unit',
        'unit/api',
        'unit/core',
        'unit/gamification',
        'unit/social',
        'unit/forum',
        'unit/chat',
        'unit/content',
        'unit/polls',
        'unit/data_management',
        'unit/api_integration'
    ]
    
    # Check directories
    missing_dirs = []
    for dir_path in expected_dirs:
        full_path = test_dir / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
        else:
            print(f"✅ {dir_path}/")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    # Check for test files
    test_files = list(test_dir.rglob("*.py"))
    test_files = [f for f in test_files if not f.name.startswith('__')]
    
    print(f"\n📄 Found {len(test_files)} test files:")
    for test_file in sorted(test_files):
        rel_path = test_file.relative_to(test_dir)
        print(f"   📄 {rel_path}")
    
    # Check for required config files
    required_files = ['conftest.py', 'README.md', '__init__.py']
    missing_files = []
    
    for req_file in required_files:
        if not (test_dir / req_file).exists():
            missing_files.append(req_file)
        else:
            print(f"✅ {req_file}")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print(f"\n✅ Test structure validation completed successfully!")
    print(f"📊 Summary:")
    print(f"   📁 Directories: {len(expected_dirs)}")
    print(f"   📄 Test files: {len(test_files)}")
    print(f"   🏗️ Structure: Organized and complete")
    
    return True

def main():
    """Main function"""
    print("🧪 Mark Foot Test Structure Validator")
    print("=" * 50)
    
    if validate_test_structure():
        print("\n🎉 All tests are properly organized!")
        sys.exit(0)
    else:
        print("\n❌ Test structure validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
