# Docker Commands for Mark Foot Project

## Build and Start Services
```bash
# Start production environment
docker-compose -f docker/docker-compose.yml up -d

# Start development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# Build and start (force rebuild)
docker-compose -f docker/docker-compose.yml up --build -d
```

## Stop Services
```bash
# Stop production environment
docker-compose -f docker/docker-compose.yml down

# Stop development environment
docker-compose -f docker/docker-compose.dev.yml down

# Stop and remove volumes
docker-compose -f docker/docker-compose.yml down -v
```

## Logs
```bash
# View all logs
docker-compose -f docker/docker-compose.yml logs

# View specific service logs
docker-compose -f docker/docker-compose.yml logs web-service
docker-compose -f docker/docker-compose.yml logs mysql_db

# Follow logs
docker-compose -f docker/docker-compose.yml logs -f web-service
```

## Access Containers
```bash
# Access Django container
docker exec -it mark_foot_web bash

# Access MySQL container
docker exec -it mark_foot_mysql mysql -u root -p

# Access MySQL with application user
docker exec -it mark_foot_mysql mysql -u mark_foot_user -p mark_foot_db
```

## Django Commands
```bash
# Run Django migrations
docker exec -it mark_foot_web python manage.py migrate

# Create superuser
docker exec -it mark_foot_web python manage.py createsuperuser

# Collect static files
docker exec -it mark_foot_web python manage.py collectstatic
```
