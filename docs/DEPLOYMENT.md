# SynQ Backend Deployment Guide

## Overview

This guide covers deploying the SynQ backend to production environments using Docker, Kubernetes, and cloud platforms.

## Prerequisites

- Docker & Docker Compose
- Kubernetes 1.24+
- Helm 3.0+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.12+

## Local Development Deployment

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/TangoSplicer/synq-backend.git
cd synq-backend

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# RabbitMQ: http://localhost:15672 (guest/guest)
```

## Production Deployment

### Kubernetes Deployment

#### 1. Build and Push Docker Image

```bash
# Build image
docker build -t your-registry/synq-backend:latest .

# Push to registry
docker push your-registry/synq-backend:latest
```

#### 2. Create Kubernetes Namespace

```bash
kubectl create namespace synq-production
```

#### 3. Create Secrets

```bash
kubectl create secret generic synq-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=jwt-secret-key="your-secret-key" \
  --from-literal=redis-url="redis://..." \
  -n synq-production
```

#### 4. Deploy with Helm

```bash
# Add Helm repository
helm repo add synq https://charts.synq.ai
helm repo update

# Install chart
helm install synq-backend synq/synq-backend \
  --namespace synq-production \
  --values values.yaml
```

#### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n synq-production

# Check services
kubectl get svc -n synq-production

# View logs
kubectl logs -f deployment/synq-backend -n synq-production
```

### Kubernetes Manifest Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synq-backend
  namespace: synq-production
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
      - name: synq-backend
        image: your-registry/synq-backend:latest
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
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: synq-secrets
              key: jwt-secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
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
  name: synq-backend
  namespace: synq-production
spec:
  selector:
    app: synq-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Cloud Platform Deployment

### AWS ECS

```bash
# Create ECS task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Create ECS service
aws ecs create-service \
  --cluster synq-production \
  --service-name synq-backend \
  --task-definition synq-backend:1 \
  --desired-count 3 \
  --load-balancers targetGroupArn=arn:aws:...,containerName=synq-backend,containerPort=8000
```

### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/synq-backend

# Deploy to Cloud Run
gcloud run deploy synq-backend \
  --image gcr.io/PROJECT_ID/synq-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...
```

### Azure Container Instances

```bash
# Create container group
az container create \
  --resource-group synq \
  --name synq-backend \
  --image your-registry/synq-backend:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=postgresql://...
```

## Database Setup

### PostgreSQL

```bash
# Create database
createdb synq_db

# Create user
createuser synq_user

# Set password
psql -c "ALTER USER synq_user WITH PASSWORD 'secure_password';"

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE synq_db TO synq_user;"

# Run migrations
alembic upgrade head
```

## Monitoring & Logging

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

### ELK Stack Logging

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/synq-backend/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Health Checks

### Liveness Probe

```bash
curl http://localhost:8000/health
```

### Readiness Probe

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Backup & Recovery

### Database Backup

```bash
# Full backup
pg_dump synq_db > backup.sql

# Compressed backup
pg_dump synq_db | gzip > backup.sql.gz

# Restore
psql synq_db < backup.sql
```

### Automated Backups

```bash
# Using pg_basebackup
pg_basebackup -h localhost -U synq_user -D /backups/synq_db -Ft -z
```

## Scaling

### Horizontal Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment synq-backend --replicas=5 -n synq-production
```

### Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: synq-backend-hpa
  namespace: synq-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: synq-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Check Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/synq-backend -n synq-production
```

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U synq_user -d synq_db -c "SELECT 1;"
```

### Redis Connection Issues

```bash
# Test connection
redis-cli ping
```

## Security Hardening

- Use TLS/SSL for all connections
- Enable authentication on all services
- Use secrets management (Vault, AWS Secrets Manager)
- Implement network policies
- Enable audit logging
- Use private container registries
- Implement rate limiting
- Enable CORS restrictions

## Support

For deployment issues, visit: https://github.com/TangoSplicer/synq-backend/issues
