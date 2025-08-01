#!/usr/bin/env python3
"""
Azure Demo Deployment Configuration
Safe demo mode for Azure within 12 hours
"""
import json
import os

def create_azure_demo_files():
    """Create Azure demo deployment configuration"""
    
    # Azure Web App configuration for demo
    demo_config = {
        "name": "trenchcoat-pro-demo",
        "resource_group": "trenchcoat-demo-rg",
        "location": "East US",
        "sku": "F1",  # Free tier for demo
        "runtime": "python|3.11",
        "settings": {
            "ENVIRONMENT": "DEMO",
            "LIVE_TRADING_ENABLED": "False",
            "DEMO_MODE": "True",
            "MAX_DEMO_COINS": "50",
            "DEMO_REFRESH_INTERVAL": "300"  # 5 minutes
        }
    }
    
    # Save configuration
    with open('azure_demo_config.json', 'w') as f:
        json.dump(demo_config, f, indent=2)
    
    # Create demo startup script
    demo_startup = """#!/bin/bash
echo "Starting TrenchCoat Pro - DEMO Mode on Azure"
echo "=========================================="

# Install dependencies
pip install -r requirements.txt

# Set demo environment
export ENVIRONMENT=DEMO
export LIVE_TRADING_ENABLED=False
export DEMO_MODE=True
export STREAMLIT_SERVER_PORT=8000
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Create demo database
python -c "
import sqlite3
conn = sqlite3.connect('data/demo_coins.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS coins (
    ticker TEXT PRIMARY KEY,
    price REAL,
    volume REAL,
    score REAL,
    demo BOOLEAN DEFAULT TRUE
)''')

# Add sample demo data
demo_coins = [
    ('DEMO1', 0.001, 50000, 0.85),
    ('DEMO2', 0.002, 100000, 0.92),
    ('DEMO3', 0.0005, 25000, 0.73)
]
for coin in demo_coins:
    cursor.execute('INSERT OR REPLACE INTO coins VALUES (?, ?, ?, ?, TRUE)', coin)
conn.commit()
conn.close()
print('Demo database created')
"

# Start application in demo mode
echo "🎯 Starting demo application..."
streamlit run app.py --server.port=8000 --server.address=0.0.0.0
"""
    
    with open('demo_startup.sh', 'w') as f:
        f.write(demo_startup)
    
    # Create quick Azure deployment script
    azure_script = """#!/bin/bash
# Quick Azure Demo Deployment (< 12 hours)

echo "🚀 Deploying TrenchCoat Pro DEMO to Azure..."

# Login to Azure
az login

# Create resource group
az group create --name trenchcoat-demo-rg --location "East US"

# Create free App Service plan
az appservice plan create \
    --name trenchcoat-demo-plan \
    --resource-group trenchcoat-demo-rg \
    --sku F1 \
    --is-linux

# Create web app
az webapp create \
    --resource-group trenchcoat-demo-rg \
    --plan trenchcoat-demo-plan \
    --name trenchcoat-pro-demo \
    --runtime "PYTHON|3.11" \
    --startup-file demo_startup.sh

# Configure demo settings
az webapp config appsettings set \
    --resource-group trenchcoat-demo-rg \
    --name trenchcoat-pro-demo \
    --settings \
        ENVIRONMENT=DEMO \
        LIVE_TRADING_ENABLED=False \
        DEMO_MODE=True

# Deploy code from local Git
az webapp deployment source config-local-git \
    --name trenchcoat-pro-demo \
    --resource-group trenchcoat-demo-rg

echo "✅ Demo deployment created!"
echo "🔗 Demo URL: https://trenchcoat-pro-demo.azurewebsites.net"
echo ""
echo "⏰ Deployment time: ~30 minutes"
echo "💰 Cost: FREE (F1 tier)"
"""
    
    with open('azure_demo_deploy.sh', 'w') as f:
        f.write(azure_script)
    
    print("✅ Azure demo deployment files created")
    print("🎯 Ready for demo deployment within 12 hours")

if __name__ == "__main__":
    create_azure_demo_files()