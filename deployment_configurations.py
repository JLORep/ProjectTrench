#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scalable Deployment Configurations
Production-ready deployment setup for 100+ API infrastructure
Created: 2025-08-02
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import os

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    host: str = "localhost"
    port: int = 5432
    database: str = "trench"
    username: str = "trench_user"
    password: str = "${DB_PASSWORD}"
    max_connections: int = 100
    connection_timeout: int = 30
    ssl_mode: str = "prefer"

@dataclass
class RedisConfig:
    """Redis configuration for caching"""
    host: str = "localhost"
    port: int = 6379
    password: str = "${REDIS_PASSWORD}"
    database: int = 0
    max_connections: int = 50
    ssl: bool = False

@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    max_requests_per_worker: int = 1000
    worker_timeout: int = 30
    keepalive: int = 2
    max_request_size: int = 10485760  # 10MB
    
@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    metrics_port: int = 9090
    health_check_path: str = "/health"
    readiness_check_path: str = "/ready"

@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 1000
    enable_api_key_auth: bool = True
    jwt_secret: str = "${JWT_SECRET}"
    encryption_key: str = "${ENCRYPTION_KEY}"

@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds

@dataclass
class DeploymentConfig:
    """Complete deployment configuration"""
    environment: str = "production"
    version: str = "1.0.0"
    
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    api: APIConfig = field(default_factory=APIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    scaling: ScalingConfig = field(default_factory=ScalingConfig)

class DeploymentManager:
    """Manages deployment configurations and generation"""
    
    def __init__(self):
        self.environments = ["development", "staging", "production"]
        self.deployment_types = ["docker", "kubernetes", "serverless", "vm"]
        
    def generate_environment_configs(self) -> Dict[str, DeploymentConfig]:
        """Generate configurations for different environments"""
        configs = {}
        
        # Development configuration
        dev_config = DeploymentConfig(
            environment="development",
            version="dev"
        )
        dev_config.database.database = "trench_dev"
        dev_config.api.workers = 1
        dev_config.security.enable_cors = True
        dev_config.scaling.min_replicas = 1
        dev_config.scaling.max_replicas = 2
        configs["development"] = dev_config
        
        # Staging configuration
        staging_config = DeploymentConfig(
            environment="staging",
            version="staging"
        )
        staging_config.database.database = "trench_staging"
        staging_config.api.workers = 2
        staging_config.scaling.min_replicas = 2
        staging_config.scaling.max_replicas = 5
        configs["staging"] = staging_config
        
        # Production configuration
        prod_config = DeploymentConfig(
            environment="production",
            version="1.0.0"
        )
        prod_config.database.type = "postgresql"
        prod_config.database.database = "trench_prod"
        prod_config.database.max_connections = 200
        prod_config.api.workers = 8
        prod_config.security.cors_origins = ["https://projecttrench.streamlit.app"]
        prod_config.scaling.min_replicas = 3
        prod_config.scaling.max_replicas = 20
        configs["production"] = prod_config
        
        return configs
    
    def generate_docker_compose(self, config: DeploymentConfig) -> str:
        """Generate Docker Compose configuration"""
        compose_config = {
            'version': '3.8',
            'services': {
                'trench-api': {
                    'build': '.',
                    'ports': [f"{config.api.port}:8000"],
                    'environment': [
                        f"ENVIRONMENT={config.environment}",
                        f"DB_HOST={config.database.host}",
                        f"DB_PORT={config.database.port}",
                        f"DB_NAME={config.database.database}",
                        f"DB_USER={config.database.username}",
                        "DB_PASSWORD=${DB_PASSWORD}",
                        f"REDIS_HOST={config.redis.host}",
                        f"REDIS_PORT={config.redis.port}",
                        "REDIS_PASSWORD=${REDIS_PASSWORD}",
                        f"WORKERS={config.api.workers}",
                        f"LOG_LEVEL={config.monitoring.log_level}"
                    ],
                    'depends_on': ['database', 'redis'],
                    'restart': 'unless-stopped',
                    'volumes': ['./data:/app/data'],
                    'networks': ['trench-network']
                },
                'database': self._get_database_service(config.database),
                'redis': {
                    'image': 'redis:7-alpine',
                    'ports': [f"{config.redis.port}:6379"],
                    'environment': ["REDIS_PASSWORD=${REDIS_PASSWORD}"],
                    'volumes': ['redis-data:/data'],
                    'restart': 'unless-stopped',
                    'networks': ['trench-network']
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': ['80:80', '443:443'],
                    'volumes': [
                        './nginx.conf:/etc/nginx/nginx.conf:ro',
                        './ssl:/etc/nginx/ssl:ro'
                    ],
                    'depends_on': ['trench-api'],
                    'restart': 'unless-stopped',
                    'networks': ['trench-network']
                }
            },
            'volumes': {
                'db-data': {},
                'redis-data': {}
            },
            'networks': {
                'trench-network': {
                    'driver': 'bridge'
                }
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False)
    
    def _get_database_service(self, db_config: DatabaseConfig) -> Dict[str, Any]:
        """Get database service configuration based on type"""
        if db_config.type == "postgresql":
            return {
                'image': 'postgres:15-alpine',
                'environment': [
                    f"POSTGRES_DB={db_config.database}",
                    f"POSTGRES_USER={db_config.username}",
                    "POSTGRES_PASSWORD=${DB_PASSWORD}"
                ],
                'ports': [f"{db_config.port}:5432"],
                'volumes': ['db-data:/var/lib/postgresql/data'],
                'restart': 'unless-stopped',
                'networks': ['trench-network']
            }
        elif db_config.type == "mysql":
            return {
                'image': 'mysql:8.0',
                'environment': [
                    f"MYSQL_DATABASE={db_config.database}",
                    f"MYSQL_USER={db_config.username}",
                    "MYSQL_PASSWORD=${DB_PASSWORD}",
                    "MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}"
                ],
                'ports': [f"{db_config.port}:3306"],
                'volumes': ['db-data:/var/lib/mysql'],
                'restart': 'unless-stopped',
                'networks': ['trench-network']
            }
        else:  # sqlite
            return {
                'image': 'alpine:latest',
                'command': 'tail -f /dev/null',  # Keep container running
                'volumes': ['./data:/app/data'],
                'networks': ['trench-network']
            }
    
    def generate_kubernetes_manifests(self, config: DeploymentConfig) -> Dict[str, str]:
        """Generate Kubernetes deployment manifests"""
        manifests = {}
        
        # Namespace
        manifests['namespace.yaml'] = yaml.dump({
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': f"trench-{config.environment}"
            }
        })
        
        # ConfigMap
        manifests['configmap.yaml'] = yaml.dump({
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': 'trench-config',
                'namespace': f"trench-{config.environment}"
            },
            'data': {
                'ENVIRONMENT': config.environment,
                'DB_HOST': config.database.host,
                'DB_PORT': str(config.database.port),
                'DB_NAME': config.database.database,
                'DB_USER': config.database.username,
                'REDIS_HOST': config.redis.host,
                'REDIS_PORT': str(config.redis.port),
                'WORKERS': str(config.api.workers),
                'LOG_LEVEL': config.monitoring.log_level
            }
        })
        
        # Secret
        manifests['secret.yaml'] = yaml.dump({
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': 'trench-secrets',
                'namespace': f"trench-{config.environment}"
            },
            'type': 'Opaque',
            'stringData': {
                'DB_PASSWORD': '${DB_PASSWORD}',
                'REDIS_PASSWORD': '${REDIS_PASSWORD}',
                'JWT_SECRET': '${JWT_SECRET}',
                'ENCRYPTION_KEY': '${ENCRYPTION_KEY}'
            }
        })
        
        # Deployment
        manifests['deployment.yaml'] = yaml.dump({
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'trench-api',
                'namespace': f"trench-{config.environment}",
                'labels': {
                    'app': 'trench-api',
                    'version': config.version
                }
            },
            'spec': {
                'replicas': config.scaling.min_replicas,
                'selector': {
                    'matchLabels': {
                        'app': 'trench-api'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'trench-api',
                            'version': config.version
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'trench-api',
                            'image': f"trench/api:{config.version}",
                            'ports': [{
                                'containerPort': 8000,
                                'name': 'http'
                            }],
                            'envFrom': [
                                {'configMapRef': {'name': 'trench-config'}},
                                {'secretRef': {'name': 'trench-secrets'}}
                            ],
                            'resources': {
                                'requests': {
                                    'cpu': '100m',
                                    'memory': '256Mi'
                                },
                                'limits': {
                                    'cpu': '1000m',
                                    'memory': '1Gi'
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': config.monitoring.health_check_path,
                                    'port': 8000
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': config.monitoring.readiness_check_path,
                                    'port': 8000
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        })
        
        # Service
        manifests['service.yaml'] = yaml.dump({
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'trench-api-service',
                'namespace': f"trench-{config.environment}"
            },
            'spec': {
                'selector': {
                    'app': 'trench-api'
                },
                'ports': [{
                    'port': 80,
                    'targetPort': 8000,
                    'protocol': 'TCP'
                }],
                'type': 'ClusterIP'
            }
        })
        
        # HorizontalPodAutoscaler
        manifests['hpa.yaml'] = yaml.dump({
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': 'trench-api-hpa',
                'namespace': f"trench-{config.environment}"
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': 'trench-api'
                },
                'minReplicas': config.scaling.min_replicas,
                'maxReplicas': config.scaling.max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': config.scaling.target_cpu_utilization
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': config.scaling.target_memory_utilization
                            }
                        }
                    }
                ],
                'behavior': {
                    'scaleUp': {
                        'stabilizationWindowSeconds': config.scaling.scale_up_cooldown
                    },
                    'scaleDown': {
                        'stabilizationWindowSeconds': config.scaling.scale_down_cooldown
                    }
                }
            }
        })
        
        return manifests
    
    def generate_dockerfile(self, config: DeploymentConfig) -> str:
        """Generate optimized Dockerfile"""
        dockerfile = f"""# Multi-stage build for TrenchCoat Pro API
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r trench && useradd -r -g trench trench

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/trench/.local

# Copy application code
COPY --chown=trench:trench . .

# Create data directory
RUN mkdir -p /app/data && chown -R trench:trench /app/data

# Switch to non-root user
USER trench

# Set environment variables
ENV PATH=/home/trench/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV WORKERS={config.api.workers}
ENV HOST={config.api.host}
ENV PORT={config.api.port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:$PORT{config.monitoring.health_check_path} || exit 1

# Expose port
EXPOSE {config.api.port}

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "${{WORKERS}}"]
"""
        return dockerfile
    
    def generate_nginx_config(self, config: DeploymentConfig) -> str:
        """Generate Nginx configuration"""
        nginx_config = f"""events {{
    worker_connections 1024;
}}

http {{
    upstream trench_api {{
        least_conn;
        server trench-api:{config.api.port} max_fails=3 fail_timeout=30s;
    }}

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate={config.security.rate_limit_per_minute}r/m;

    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    server {{
        listen 80;
        server_name _;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }}

    server {{
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # API endpoints
        location /api/ {{
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://trench_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }}

        # Health checks
        location {config.monitoring.health_check_path} {{
            proxy_pass http://trench_api;
            access_log off;
        }}

        location {config.monitoring.readiness_check_path} {{
            proxy_pass http://trench_api;
            access_log off;
        }}

        # Static files (if any)
        location /static/ {{
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
}}
"""
        return nginx_config
    
    def generate_systemd_service(self, config: DeploymentConfig) -> str:
        """Generate systemd service file for VM deployment"""
        service_config = f"""[Unit]
Description=TrenchCoat Pro API Service
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=exec
User=trench
Group=trench
WorkingDirectory=/opt/trench
Environment=ENVIRONMENT={config.environment}
Environment=DB_HOST={config.database.host}
Environment=DB_PORT={config.database.port}
Environment=DB_NAME={config.database.database}
Environment=DB_USER={config.database.username}
Environment=REDIS_HOST={config.redis.host}
Environment=REDIS_PORT={config.redis.port}
Environment=WORKERS={config.api.workers}
Environment=LOG_LEVEL={config.monitoring.log_level}
EnvironmentFile=-/etc/trench/secrets.env

ExecStart=/opt/trench/venv/bin/python -m uvicorn main:app --host {config.api.host} --port {config.api.port} --workers {config.api.workers}
ExecReload=/bin/kill -HUP $MAINPID

Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/trench/data /var/log/trench

# Resource limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
"""
        return service_config
    
    def save_deployment_files(self, environment: str = "production"):
        """Save all deployment files for specified environment"""
        configs = self.generate_environment_configs()
        config = configs[environment]
        
        # Create deployment directory
        deploy_dir = Path(f"deployment/{environment}")
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration as JSON
        with open(deploy_dir / "config.json", 'w') as f:
            json.dump(asdict(config), f, indent=2)
        
        # Save Docker Compose
        with open(deploy_dir / "docker-compose.yml", 'w') as f:
            f.write(self.generate_docker_compose(config))
        
        # Save Dockerfile
        with open(deploy_dir / "Dockerfile", 'w') as f:
            f.write(self.generate_dockerfile(config))
        
        # Save Nginx config
        with open(deploy_dir / "nginx.conf", 'w') as f:
            f.write(self.generate_nginx_config(config))
        
        # Save systemd service
        with open(deploy_dir / "trench-api.service", 'w') as f:
            f.write(self.generate_systemd_service(config))
        
        # Save Kubernetes manifests
        k8s_dir = deploy_dir / "kubernetes"
        k8s_dir.mkdir(exist_ok=True)
        
        manifests = self.generate_kubernetes_manifests(config)
        for filename, content in manifests.items():
            with open(k8s_dir / filename, 'w') as f:
                f.write(content)
        
        # Save environment file template
        with open(deploy_dir / ".env.template", 'w') as f:
            f.write(self._generate_env_template(config))
        
        # Save deployment instructions
        with open(deploy_dir / "DEPLOYMENT.md", 'w') as f:
            f.write(self._generate_deployment_instructions(environment, config))
        
        print(f"Deployment files saved to: {deploy_dir}")
        
        return deploy_dir
    
    def _generate_env_template(self, config: DeploymentConfig) -> str:
        """Generate environment variables template"""
        return f"""# TrenchCoat Pro Environment Configuration
# Environment: {config.environment}

# Database
DB_PASSWORD=your_secure_database_password
DB_ROOT_PASSWORD=your_root_password

# Redis
REDIS_PASSWORD=your_redis_password

# Security
JWT_SECRET=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# API Keys (add your provider API keys)
COINGECKO_API_KEY=your_coingecko_api_key
CMC_API_KEY=your_coinmarketcap_api_key
MORALIS_API_KEY=your_moralis_api_key
BIRDEYE_API_KEY=your_birdeye_api_key
ETHERSCAN_API_KEY=your_etherscan_api_key

# Monitoring (optional)
SENTRY_DSN=your_sentry_dsn
DATADOG_API_KEY=your_datadog_api_key

# Discord Webhooks
DISCORD_WEBHOOK_URL=your_discord_webhook_url
"""
    
    def _generate_deployment_instructions(self, environment: str, config: DeploymentConfig) -> str:
        """Generate deployment instructions"""
        return f"""# TrenchCoat Pro Deployment Guide - {environment.title()}

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
   cp deployment/{environment}/.env.template .env
   ```

2. **Configure Environment:**
   Edit `.env` file with your actual values:
   - Database passwords
   - API keys for crypto providers
   - JWT secrets
   - Redis password

3. **Deploy:**
   ```bash
   docker-compose -f deployment/{environment}/docker-compose.yml up -d
   ```

4. **Verify Deployment:**
   ```bash
   curl http://localhost:{config.api.port}{config.monitoring.health_check_path}
   ```

## Kubernetes Deployment

1. **Apply Manifests:**
   ```bash
   kubectl apply -f deployment/{environment}/kubernetes/
   ```

2. **Check Status:**
   ```bash
   kubectl get pods -n trench-{environment}
   kubectl get svc -n trench-{environment}
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
   sudo cp deployment/{environment}/trench-api.service /etc/systemd/system/
   
   # Copy nginx config
   sudo cp deployment/{environment}/nginx.conf /etc/nginx/sites-available/trench
   sudo ln -s /etc/nginx/sites-available/trench /etc/nginx/sites-enabled/
   
   # Start services
   sudo systemctl enable trench-api
   sudo systemctl start trench-api
   sudo systemctl reload nginx
   ```

## Configuration

### Database Configuration
- **Type:** {config.database.type}
- **Max Connections:** {config.database.max_connections}
- **Connection Timeout:** {config.database.connection_timeout}s

### API Configuration
- **Workers:** {config.api.workers}
- **Port:** {config.api.port}
- **Max Request Size:** {config.api.max_request_size} bytes

### Scaling Configuration
- **Min Replicas:** {config.scaling.min_replicas}
- **Max Replicas:** {config.scaling.max_replicas}
- **CPU Target:** {config.scaling.target_cpu_utilization}%
- **Memory Target:** {config.scaling.target_memory_utilization}%

## Monitoring

### Health Checks
- **Health:** `GET {config.monitoring.health_check_path}`
- **Readiness:** `GET {config.monitoring.readiness_check_path}`

### Metrics
- **Port:** {config.monitoring.metrics_port}
- **Endpoint:** `/metrics`

### Logs
- **Level:** {config.monitoring.log_level}
- **Format:** JSON structured logging

## Security

### CORS Configuration
- **Enabled:** {config.security.enable_cors}
- **Origins:** {config.security.cors_origins}

### Rate Limiting
- **Enabled:** {config.security.enable_rate_limiting}
- **Limit:** {config.security.rate_limit_per_minute}/minute

### Authentication
- **API Key Auth:** {config.security.enable_api_key_auth}
- **JWT Secret:** Required in environment

## Troubleshooting

### Common Issues

1. **Database Connection Refused:**
   ```bash
   # Check database status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h {config.database.host} -p {config.database.port} -U {config.database.username} -d {config.database.database}
   ```

2. **Redis Connection Failed:**
   ```bash
   # Check Redis status
   sudo systemctl status redis
   
   # Test connection
   redis-cli -h {config.redis.host} -p {config.redis.port} ping
   ```

3. **High Memory Usage:**
   ```bash
   # Check memory usage
   docker stats  # For Docker
   kubectl top pods -n trench-{environment}  # For Kubernetes
   ```

4. **API Timeouts:**
   - Check rate limiting configuration
   - Verify API provider credentials
   - Monitor network connectivity

### Log Locations
- **Docker:** `docker logs <container_id>`
- **Kubernetes:** `kubectl logs -n trench-{environment} <pod_name>`
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
kubectl rollout restart deployment/trench-api -n trench-{environment}  # Kubernetes
sudo systemctl restart trench-api  # SystemD
```

### Backup
```bash
# Database backup
pg_dump -h {config.database.host} -U {config.database.username} {config.database.database} > backup.sql

# Redis backup
redis-cli -h {config.redis.host} -p {config.redis.port} SAVE
```

### Scaling
```bash
# Docker Compose
docker-compose up -d --scale trench-api=5

# Kubernetes (HPA handles this automatically)
kubectl scale deployment trench-api --replicas=5 -n trench-{environment}
```

## Support

For issues and support:
- GitHub Issues: https://github.com/your-org/trench-api/issues
- Documentation: https://docs.trenchpro.com
- Discord: https://discord.gg/trenchpro
"""

# CLI interface
if __name__ == "__main__":
    import sys
    
    def main():
        manager = DeploymentManager()
        
        if len(sys.argv) > 1:
            environment = sys.argv[1]
            if environment not in manager.environments:
                print(f"Invalid environment. Choose from: {manager.environments}")
                sys.exit(1)
        else:
            environment = "production"
        
        print(f"Generating deployment configurations for {environment}...")
        
        # Generate and save all deployment files
        deploy_dir = manager.save_deployment_files(environment)
        
        print(f"\n✅ Deployment files generated successfully!")
        print(f"📁 Location: {deploy_dir}")
        print(f"\n📋 Next steps:")
        print(f"1. Copy .env.template to .env and configure your secrets")
        print(f"2. Follow instructions in DEPLOYMENT.md")
        print(f"3. Deploy using your preferred method (Docker/Kubernetes/VM)")
        
        # Show summary
        configs = manager.generate_environment_configs()
        config = configs[environment]
        
        print(f"\n📊 Configuration Summary:")
        print(f"- Environment: {config.environment}")
        print(f"- Database: {config.database.type}")
        print(f"- API Workers: {config.api.workers}")
        print(f"- Scaling: {config.scaling.min_replicas}-{config.scaling.max_replicas} replicas")
        print(f"- Security: CORS {'enabled' if config.security.enable_cors else 'disabled'}")
        
    main()