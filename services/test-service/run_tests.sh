#!/bin/bash

# Test Runner Script for Mark Foot Test Service
# Usage: ./run_tests.sh [test_type] [options]

set -e

# Default values
TEST_TYPE="all"
COVERAGE=true
PARALLEL=false
VERBOSE=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --quiet)
            VERBOSE=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --type TYPE        Test type: all, unit, integration, auth, api (default: all)"
            echo "  --no-coverage      Disable coverage reporting"
            echo "  --parallel         Run tests in parallel"
            echo "  --quiet            Reduce output verbosity"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=html --cov-report=term-missing"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Add test type filter
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD -m unit unit/"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD -m integration integration/"
        ;;
    auth)
        PYTEST_CMD="$PYTEST_CMD -m auth auth/"
        ;;
    api)
        PYTEST_CMD="$PYTEST_CMD -m api"
        ;;
    gamification)
        PYTEST_CMD="$PYTEST_CMD -m gamification unit/gamification/"
        ;;
    social)
        PYTEST_CMD="$PYTEST_CMD -m social unit/social/"
        ;;
    data)
        PYTEST_CMD="$PYTEST_CMD -m data data/"
        ;;
    all)
        # Run all tests
        ;;
    *)
        echo "Unknown test type: $TEST_TYPE"
        echo "Valid types: all, unit, integration, auth, api, gamification, social, data"
        exit 1
        ;;
esac

echo "🧪 Running Mark Foot Tests"
echo "Test Type: $TEST_TYPE"
echo "Coverage: $COVERAGE"
echo "Parallel: $PARALLEL"
echo "Command: $PYTEST_CMD"
echo ""

# Set Django settings
export DJANGO_SETTINGS_MODULE=test_settings

# Run tests
eval $PYTEST_CMD

echo ""
echo "✅ Tests completed!"

if [ "$COVERAGE" = true ]; then
    echo "📊 Coverage report generated in htmlcov/index.html"
fi
