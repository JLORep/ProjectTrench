#!/usr/bin/env python3
"""
STREAMLIT CLOUD DEPLOYMENT CONFIGURATION
Deploy TrenchCoat Elite Pro to public website
"""
import streamlit as st
import os
from pathlib import Path

# Streamlit Cloud deployment settings
STREAMLIT_CONFIG = {
    'app_name': 'trenchcoat-elite-pro',
    'github_repo': 'https://github.com/your-username/trenchcoat-elite',
    'main_file': 'enhanced_dashboard.py',
    'python_version': '3.11',
    'requirements': [
        'streamlit>=1.47.0',
        'plotly>=6.2.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'aiohttp>=3.8.0',
        'asyncio-mqtt>=0.14.0',
        'loguru>=0.7.0',
        'anthropic>=0.25.0',
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0',
        'sqlite3',  # Built-in
        'datetime',  # Built-in
        'json',     # Built-in
        'hashlib',  # Built-in
        'pydantic>=2.5.0',
        'python-multipart>=0.0.6'
    ]
}

def create_deployment_files():
    """Create necessary deployment files"""
    
    # Create requirements.txt
    with open('requirements.txt', 'w') as f:
        for req in STREAMLIT_CONFIG['requirements']:
            if req not in ['sqlite3', 'datetime', 'json', 'hashlib']:
                f.write(f"{req}\n")
    
    # Create .streamlit/config.toml
    os.makedirs('.streamlit', exist_ok=True)
    with open('.streamlit/config.toml', 'w') as f:
        f.write("""
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
base = "dark"
primaryColor = "#10b981"
backgroundColor = "#111827"
secondaryBackgroundColor = "#1f2937"
textColor = "#f9fafb"

[client]
toolbarMode = "minimal"
showErrorDetails = true
""")
    
    # Create .gitignore
    with open('.gitignore', 'w') as f:
        f.write("""
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.streamlit/secrets.toml
*.db
logs/
data/backups/
*.env
.env.local
.env.*.local
node_modules/
""")
    
    # Create Procfile for Heroku deployment (alternative)
    with open('Procfile', 'w') as f:
        f.write('web: streamlit run enhanced_dashboard.py --server.port=$PORT --server.address=0.0.0.0\n')
    
    # Create runtime.txt for Python version
    with open('runtime.txt', 'w') as f:
        f.write('python-3.11.0\n')
    
    print("✅ Deployment files created successfully!")
    print("\n📋 Next steps:")
    print("1. Create GitHub repository")
    print("2. Push all files to GitHub")
    print("3. Connect to Streamlit Cloud")
    print("4. Deploy at: https://share.streamlit.io/")

def create_docker_deployment():
    """Create Docker deployment option"""
    dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "enhanced_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    docker_compose_content = """
version: '3.8'
services:
  trenchcoat:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_THEME_BASE=dark
      - STREAMLIT_THEME_PRIMARY_COLOR=#10b981
    volumes:
      - ./data:/app/data
    restart: unless-stopped
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)
    
    print("✅ Docker deployment files created!")
    print("Run with: docker-compose up -d")

if __name__ == "__main__":
    create_deployment_files()
    create_docker_deployment()