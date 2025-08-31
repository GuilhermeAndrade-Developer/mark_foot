#!/bin/bash

# ============================================================================
# MARK FOOT - PRODUCTION DEPLOYMENT SCRIPT
# ============================================================================
# Deploy script for AWS/GCP cloud environments
# Usage: ./deploy.sh [aws|gcp]

set -e  # Exit on any error

CLOUD_PROVIDER=${1:-aws}
PROJECT_NAME="mark-foot"
ENVIRONMENT="production"

echo "🚀 Starting deployment for $CLOUD_PROVIDER..."

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

echo "🔍 Running pre-deployment checks..."

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ ERROR: .env.prod file not found!"
    echo "📋 Please copy .env.prod.template to .env.prod and configure it"
    exit 1
fi

# Check if required environment variables are set
source .env.prod

required_vars=(
    "SECRET_KEY"
    "DB_HOST"
    "DB_PASSWORD"
    "STRIPE_SECRET_KEY"
    "PAGSEGURO_TOKEN"
    "FRONTEND_URL"
    "BACKEND_URL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: Required environment variable $var is not set in .env.prod"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# ============================================================================
# BUILD AND TEST
# ============================================================================

echo "🏗️ Building application..."

# Build Docker images
docker-compose -f docker/docker-compose.prod.yml build

echo "🧪 Running tests..."

# Run tests
docker-compose -f docker/docker-compose.test.yml up --abort-on-container-exit
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "❌ Tests failed! Deployment aborted."
    exit 1
fi

echo "✅ All tests passed"

# ============================================================================
# CLOUD-SPECIFIC DEPLOYMENT
# ============================================================================

case $CLOUD_PROVIDER in
    "aws")
        echo "☁️ Deploying to AWS..."
        
        # AWS ECS/EC2 deployment
        echo "📦 Pushing images to ECR..."
        
        # Login to ECR
        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
        
        # Tag and push images
        docker tag mark_foot_web_prod:latest $ECR_REGISTRY/mark-foot-web:latest
        docker tag mark_foot_frontend_prod:latest $ECR_REGISTRY/mark-foot-frontend:latest
        
        docker push $ECR_REGISTRY/mark-foot-web:latest
        docker push $ECR_REGISTRY/mark-foot-frontend:latest
        
        # Deploy to ECS
        echo "🚀 Deploying to ECS..."
        aws ecs update-service --cluster $ECS_CLUSTER --service mark-foot-web --force-new-deployment
        aws ecs update-service --cluster $ECS_CLUSTER --service mark-foot-frontend --force-new-deployment
        
        echo "✅ AWS deployment completed"
        ;;
        
    "gcp")
        echo "☁️ Deploying to GCP..."
        
        # GCP Cloud Run deployment
        echo "📦 Pushing images to GCR..."
        
        # Configure Docker for GCR
        gcloud auth configure-docker
        
        # Tag and push images
        docker tag mark_foot_web_prod:latest gcr.io/$GCP_PROJECT_ID/mark-foot-web:latest
        docker tag mark_foot_frontend_prod:latest gcr.io/$GCP_PROJECT_ID/mark-foot-frontend:latest
        
        docker push gcr.io/$GCP_PROJECT_ID/mark-foot-web:latest
        docker push gcr.io/$GCP_PROJECT_ID/mark-foot-frontend:latest
        
        # Deploy to Cloud Run
        echo "🚀 Deploying to Cloud Run..."
        gcloud run deploy mark-foot-web \
            --image gcr.io/$GCP_PROJECT_ID/mark-foot-web:latest \
            --platform managed \
            --region $GCP_REGION \
            --allow-unauthenticated \
            --port 8000 \
            --memory 1Gi \
            --cpu 1 \
            --max-instances 10
            
        gcloud run deploy mark-foot-frontend \
            --image gcr.io/$GCP_PROJECT_ID/mark-foot-frontend:latest \
            --platform managed \
            --region $GCP_REGION \
            --allow-unauthenticated \
            --port 80 \
            --memory 512Mi \
            --cpu 0.5 \
            --max-instances 5
        
        echo "✅ GCP deployment completed"
        ;;
        
    *)
        echo "❌ Unsupported cloud provider: $CLOUD_PROVIDER"
        echo "Supported providers: aws, gcp"
        exit 1
        ;;
esac

# ============================================================================
# POST-DEPLOYMENT TASKS
# ============================================================================

echo "🔧 Running post-deployment tasks..."

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "📊 Running database migrations..."
case $CLOUD_PROVIDER in
    "aws")
        aws ecs run-task \
            --cluster $ECS_CLUSTER \
            --task-definition mark-foot-migration \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],assignPublicIp=ENABLED}"
        ;;
    "gcp")
        gcloud run jobs create mark-foot-migration \
            --image gcr.io/$GCP_PROJECT_ID/mark-foot-web:latest \
            --region $GCP_REGION \
            --task-override='{"spec":{"template":{"spec":{"template":{"spec":{"containers":[{"command":["python","manage.py","migrate"]}]}}}}}}'
        gcloud run jobs execute mark-foot-migration --region $GCP_REGION
        ;;
esac

# Health checks
echo "🏥 Running health checks..."
BACKEND_URL=${BACKEND_URL}
FRONTEND_URL=${FRONTEND_URL}

# Check backend health
backend_status=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health/")
if [ "$backend_status" != "200" ]; then
    echo "⚠️ WARNING: Backend health check failed (HTTP $backend_status)"
else
    echo "✅ Backend is healthy"
fi

# Check frontend
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$frontend_status" != "200" ]; then
    echo "⚠️ WARNING: Frontend health check failed (HTTP $frontend_status)"
else
    echo "✅ Frontend is healthy"
fi

# Test payment endpoints
echo "💳 Testing payment endpoints..."
payment_test=$(curl -s -X POST "$BACKEND_URL/api/billing/api/payments/test_payment_connection/" \
    -H "Content-Type: application/json" \
    -d '{"gateway": "all"}' \
    -w "%{http_code}")

if [[ "$payment_test" == *"200"* ]]; then
    echo "✅ Payment gateways are responding"
else
    echo "⚠️ WARNING: Payment endpoints may have issues"
fi

# ============================================================================
# COMPLETION
# ============================================================================

echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo ""
echo "📋 Deployment Summary:"
echo "   Cloud Provider: $CLOUD_PROVIDER"
echo "   Environment: $ENVIRONMENT"
echo "   Frontend URL: $FRONTEND_URL"
echo "   Backend URL: $BACKEND_URL"
echo ""
echo "🔗 Important URLs:"
echo "   Frontend: $FRONTEND_URL"
echo "   Admin Panel: $BACKEND_URL/admin/"
echo "   API Documentation: $BACKEND_URL/api/docs/"
echo "   Payment Webhooks:"
echo "     Stripe: $BACKEND_URL/api/billing/api/webhooks/stripe/"
echo "     PagSeguro: $BACKEND_URL/api/billing/api/webhooks/pagseguro/"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure DNS to point to your deployed services"
echo "   2. Set up SSL certificates (Let's Encrypt/CloudFlare)"
echo "   3. Configure payment webhook URLs in Stripe/PagSeguro dashboards"
echo "   4. Set up monitoring and alerting"
echo "   5. Configure backup schedules for database"
echo ""
echo "🎊 Your Mark Foot application is now live in production!"
