# Full Stack Deployment Guide - Frontend + Backend

## Overview

This guide provides comprehensive instructions for deploying the complete SynQ platform, including both the frontend showcase website and the backend API.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Load Balancer                         │
│              (SSL/TLS Termination)                      │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────┐
│   Frontend   │  │    Backend    │
│   (React)    │  │   (FastAPI)   │
│   Port 3000  │  │   Port 8000   │
└───────┬──────┘  └──────┬────────┘
        │                │
        └────────┬───────┘
                 │
        ┌────────▼────────┐
        │  PostgreSQL DB  │
        │   Redis Cache   │
        │  RabbitMQ Queue │
        └─────────────────┘
```

## Prerequisites

### System Requirements
- Ubuntu 22.04 LTS or equivalent
- 8+ CPU cores
- 16GB+ RAM
- 100GB+ storage
- Docker & Docker Compose installed
- kubectl (for Kubernetes deployments)

### Domain Setup
- Frontend domain: `synq-expansion-showcase.manus.space`
- Backend domain: `api.synq.manus.space`
- SSL certificates (Let's Encrypt recommended)

## Deployment Options

### Option 1: Docker Compose (Development/Small Scale)

#### Step 1: Clone Repositories

```bash
# Clone backend
git clone https://github.com/TangoSplicer/synq-backend.git
cd synq-backend

# Clone frontend (in separate directory)
cd ..
git clone https://github.com/TangoSplicer/synq_expansion_showcase.git
```

#### Step 2: Configure Environment

**Backend (.env)**:
```bash
cd synq-backend
cp .env.example .env

# Edit .env with your settings
ENVIRONMENT=production
DATABASE_URL=postgresql://synq:password@postgres:5432/synq
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:3000
```

**Frontend (.env)**:
```bash
cd ../synq_expansion_showcase
cp .env.example .env

# Edit .env with your settings
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=SynQ Platform
```

#### Step 3: Create Docker Compose Override

```bash
# In synq-backend directory
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: synq
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: synq
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports:
      - "5672:5672"
      - "15672:15672"

  backend:
    build:
      context: ./synq-backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://synq:secure_password@postgres:5432/synq
      REDIS_URL: redis://redis:6379/0
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis
      - rabbitmq

  frontend:
    build:
      context: ./synq_expansion_showcase
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
EOF
```

#### Step 4: Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Step 5: Verify Deployment

```bash
# Check services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Option 2: Kubernetes (Production Scale)

#### Step 1: Create Kubernetes Manifests

**Backend Deployment (k8s/backend-deployment.yaml)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synq-backend
  namespace: synq
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synq-backend
  template:
    metadata:
      labels:
        app: synq-backend
    spec:
      containers:
      - name: backend
        image: synq-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: synq-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: synq-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: synq-backend-service
  namespace: synq
spec:
  selector:
    app: synq-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

**Frontend Deployment (k8s/frontend-deployment.yaml)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synq-frontend
  namespace: synq
spec:
  replicas: 2
  selector:
    matchLabels:
      app: synq-frontend
  template:
    metadata:
      labels:
        app: synq-frontend
    spec:
      containers:
      - name: frontend
        image: synq-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: VITE_API_BASE_URL
          value: "https://api.synq.manus.space"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: synq-frontend-service
  namespace: synq
spec:
  selector:
    app: synq-frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
  type: LoadBalancer
```

#### Step 2: Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace synq

# Create secrets
kubectl create secret generic synq-secrets \
  --from-literal=database-url='postgresql://synq:password@postgres:5432/synq' \
  --from-literal=redis-url='redis://redis:6379/0' \
  -n synq
```

#### Step 3: Deploy to Kubernetes

```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Check deployment status
kubectl get deployments -n synq
kubectl get services -n synq
```

### Option 3: Cloud Platforms

#### AWS Deployment

**Backend**:
- ECS (Elastic Container Service) for containerized backend
- RDS (Relational Database Service) for PostgreSQL
- ElastiCache for Redis
- ALB (Application Load Balancer) for routing

**Frontend**:
- CloudFront for CDN
- S3 for static assets
- Route 53 for DNS

#### GCP Deployment

**Backend**:
- Cloud Run for containerized backend
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Load Balancing

**Frontend**:
- Cloud CDN
- Cloud Storage for static assets
- Cloud DNS

#### Azure Deployment

**Backend**:
- Container Instances for backend
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Application Gateway

**Frontend**:
- Azure CDN
- Blob Storage for static assets
- Azure DNS

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificates
sudo certbot certonly --standalone \
  -d synq-expansion-showcase.manus.space \
  -d api.synq.manus.space

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/synq

# Backend API
upstream backend {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name api.synq.manus.space;

    ssl_certificate /etc/letsencrypt/live/api.synq.manus.space/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.synq.manus.space/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend Website
upstream frontend {
    server localhost:3000;
}

server {
    listen 443 ssl http2;
    server_name synq-expansion-showcase.manus.space;

    ssl_certificate /etc/letsencrypt/live/synq-expansion-showcase.manus.space/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/synq-expansion-showcase.manus.space/privkey.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name api.synq.manus.space synq-expansion-showcase.manus.space;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Logging

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'synq-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### ELK Stack Setup

```bash
# Docker Compose for ELK
docker-compose -f docker-compose.elk.yml up -d
```

### Grafana Dashboard

Access Grafana at `http://localhost:3000` and import dashboards for:
- Backend API metrics
- Database performance
- Cache hit rates
- Job execution times

## Health Checks

### Backend Health Check

```bash
curl https://api.synq.manus.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "message_broker": "connected"
}
```

### Frontend Health Check

```bash
curl https://synq-expansion-showcase.manus.space
```

Expected: HTTP 200 with HTML content

## Backup and Recovery

### Database Backup

```bash
# Backup PostgreSQL
pg_dump -h localhost -U synq synq > backup.sql

# Restore
psql -h localhost -U synq synq < backup.sql
```

### Redis Backup

```bash
# Backup Redis
redis-cli BGSAVE

# Copy dump.rdb to safe location
cp /var/lib/redis/dump.rdb /backups/redis-backup.rdb
```

## Scaling Considerations

### Horizontal Scaling

- **Backend**: Scale to 3-5 replicas for load distribution
- **Frontend**: Scale to 2-3 replicas for redundancy
- **Database**: Use read replicas for read-heavy operations

### Vertical Scaling

- **Backend**: Increase CPU/memory for compute-heavy operations
- **Database**: Increase storage and memory for large datasets
- **Cache**: Increase Redis memory for higher cache capacity

## Performance Optimization

### Caching Strategy

- Frontend assets cached via CloudFront/CDN
- API responses cached in Redis (5-60 minutes TTL)
- Database query results cached (5-10 minutes TTL)

### Database Optimization

- Create indexes on frequently queried columns
- Use connection pooling (min: 10, max: 100)
- Enable query caching for read-heavy operations

### API Rate Limiting

- Authenticated users: 1,000 req/min
- Anonymous users: 100 req/min
- VQE/QAOA execution: 10 req/min

## Disaster Recovery

### RTO (Recovery Time Objective): 1 hour
### RPO (Recovery Point Objective): 15 minutes

### Recovery Procedures

1. **Database Failure**:
   - Restore from latest backup
   - Verify data integrity
   - Restart backend services

2. **Backend Service Failure**:
   - Kubernetes automatically restarts failed pods
   - Load balancer routes traffic to healthy instances

3. **Frontend Service Failure**:
   - CDN serves cached content
   - Kubernetes automatically restarts failed pods

## Deployment Checklist

- [ ] Domains configured and DNS records updated
- [ ] SSL/TLS certificates installed
- [ ] Environment variables configured
- [ ] Database initialized and migrated
- [ ] Redis cache configured
- [ ] RabbitMQ message broker configured
- [ ] Backend deployed and running
- [ ] Frontend deployed and running
- [ ] Health checks passing
- [ ] Monitoring and logging enabled
- [ ] Backup procedures configured
- [ ] Disaster recovery plan tested
- [ ] Load balancing configured
- [ ] Rate limiting enabled
- [ ] CORS configured correctly

## Troubleshooting

### Backend Connection Issues
```bash
# Check backend logs
docker-compose logs backend

# Verify database connection
psql -h localhost -U synq -d synq -c "SELECT 1"

# Check Redis connection
redis-cli ping
```

### Frontend Connection Issues
```bash
# Check frontend logs
docker-compose logs frontend

# Verify API connectivity
curl -v https://api.synq.manus.space/health
```

### SSL/TLS Issues
```bash
# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/api.synq.manus.space/fullchain.pem -noout -dates

# Renew certificates
sudo certbot renew --force-renewal
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review documentation: https://synq-expansion-showcase.manus.space
3. Open GitHub issue: https://github.com/TangoSplicer/synq-backend/issues
4. Contact support team

---

**Last Updated**: 2025-01-04
**Version**: 4.0.0
