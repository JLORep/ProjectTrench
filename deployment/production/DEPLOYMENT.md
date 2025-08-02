# TrenchCoat Pro Deployment Guide - Production

## Prerequisites

1. **System Requirements:**
   - CPU: 4+ cores (8+ recommended for production)
   - RAM: 8GB+ (16GB+ recommended for production)
   - Storage: 100GB+ SSD
   - Network: High-bandwidth internet connection

2. **Software Requirements:**
   - Docker & Docker Compose
   - Python 3.11+
   - PostgreSQL 15+ (for production)
   - Redis 7+
   - Nginx (for reverse proxy)

## Quick Start with Docker Compose

1. **Clone and Setup:**
   ```bash
   git clone https://github.com/your-org/trench-api.git
   cd trench-api
   cp deployment/production/.env.template .env
   ```

2. **Configure Environment:**
   Edit `.env` file with your actual values:
   - Database passwords
   - API keys for crypto providers
   - JWT secrets
   - Redis password

3. **Deploy:**
   ```bash
   docker-compose -f deployment/production/docker-compose.yml up -d
   ```

4. **Verify Deployment:**
   ```bash
   curl http://localhost:8000/health
   ```

## Kubernetes Deployment

1. **Apply Manifests:**
   ```bash
   kubectl apply -f deployment/production/kubernetes/
   ```

2. **Check Status:**
   ```bash
   kubectl get pods -n trench-production
   kubectl get svc -n trench-production
   ```

## VM/Bare Metal Deployment

1. **System Setup:**
   ```bash
   # Create user
   sudo useradd -m -s /bin/bash trench
   
   # Install dependencies
   sudo apt update
   sudo apt install python3.11 python3.11-venv postgresql redis-server nginx
   ```

2. **Application Setup:**
   ```bash
   # Setup application
   sudo mkdir -p /opt/trench
   sudo chown trench:trench /opt/trench
   
   # Clone and install
   git clone https://github.com/your-org/trench-api.git /opt/trench
   cd /opt/trench
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Services:**
   ```bash
   # Copy service file
   sudo cp deployment/production/trench-api.service /etc/systemd/system/
   
   # Copy nginx config
   sudo cp deployment/production/nginx.conf /etc/nginx/sites-available/trench
   sudo ln -s /etc/nginx/sites-available/trench /etc/nginx/sites-enabled/
   
   # Start services
   sudo systemctl enable trench-api
   sudo systemctl start trench-api
   sudo systemctl reload nginx
   ```

## Configuration

### Database Configuration
- **Type:** postgresql
- **Max Connections:** 200
- **Connection Timeout:** 30s

### API Configuration
- **Workers:** 8
- **Port:** 8000
- **Max Request Size:** 10485760 bytes

### Scaling Configuration
- **Min Replicas:** 3
- **Max Replicas:** 20
- **CPU Target:** 70%
- **Memory Target:** 80%

## Monitoring

### Health Checks
- **Health:** `GET /health`
- **Readiness:** `GET /ready`

### Metrics
- **Port:** 9090
- **Endpoint:** `/metrics`

### Logs
- **Level:** INFO
- **Format:** JSON structured logging

## Security

### CORS Configuration
- **Enabled:** True
- **Origins:** ['https://projecttrench.streamlit.app']

### Rate Limiting
- **Enabled:** True
- **Limit:** 1000/minute

### Authentication
- **API Key Auth:** True
- **JWT Secret:** Required in environment

## Troubleshooting

### Common Issues

1. **Database Connection Refused:**
   ```bash
   # Check database status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -p 5432 -U trench_user -d trench_prod
   ```

2. **Redis Connection Failed:**
   ```bash
   # Check Redis status
   sudo systemctl status redis
   
   # Test connection
   redis-cli -h localhost -p 6379 ping
   ```

3. **High Memory Usage:**
   ```bash
   # Check memory usage
   docker stats  # For Docker
   kubectl top pods -n trench-production  # For Kubernetes
   ```

4. **API Timeouts:**
   - Check rate limiting configuration
   - Verify API provider credentials
   - Monitor network connectivity

### Log Locations
- **Docker:** `docker logs <container_id>`
- **Kubernetes:** `kubectl logs -n trench-production <pod_name>`
- **SystemD:** `journalctl -u trench-api -f`

### Performance Tuning

1. **Database Optimization:**
   - Tune connection pool size
   - Enable query caching
   - Add appropriate indexes

2. **API Optimization:**
   - Adjust worker count based on CPU cores
   - Tune request timeout values
   - Enable compression

3. **Caching Optimization:**
   - Increase Redis memory limit
   - Tune cache TTL values
   - Monitor cache hit rates

## Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Restart services
docker-compose restart  # Docker
kubectl rollout restart deployment/trench-api -n trench-production  # Kubernetes
sudo systemctl restart trench-api  # SystemD
```

### Backup
```bash
# Database backup
pg_dump -h localhost -U trench_user trench_prod > backup.sql

# Redis backup
redis-cli -h localhost -p 6379 SAVE
```

### Scaling
```bash
# Docker Compose
docker-compose up -d --scale trench-api=5

# Kubernetes (HPA handles this automatically)
kubectl scale deployment trench-api --replicas=5 -n trench-production
```

## Support

For issues and support:
- GitHub Issues: https://github.com/your-org/trench-api/issues
- Documentation: https://docs.trenchpro.com
- Discord: https://discord.gg/trenchpro
