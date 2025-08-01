#!/bin/bash
# Azure Deployment Script for TrenchCoat Elite Pro

echo "🚀 Starting Azure deployment..."

# 1. Login to Azure (if not already logged in)
az login

# 2. Create resource group
az group create --name trenchcoat-rg --location "East US"

# 3. Create App Service plan
az appservice plan create \
    --name trenchcoat-plan \
    --resource-group trenchcoat-rg \
    --sku B2 \
    --is-linux

# 4. Create web app
az webapp create \
    --resource-group trenchcoat-rg \
    --plan trenchcoat-plan \
    --name trenchcoat-elite-pro \
    --runtime "PYTHON|3.11" \
    --startup-file startup.sh

# 5. Configure app settings
az webapp config appsettings set \
    --resource-group trenchcoat-rg \
    --name trenchcoat-elite-pro \
    --settings \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        STREAMLIT_SERVER_PORT=8000 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        PYTHON_VERSION=3.11

# 6. Deploy from GitHub (manual step - configure in Azure Portal)
echo "✅ Azure resources created successfully!"
echo "🔗 App URL: https://trenchcoat-elite-pro.azurewebsites.net"
echo ""
echo "📋 Manual steps remaining:"
echo "1. Connect GitHub repository in Azure Portal"
echo "2. Add API keys to Configuration > Application Settings"
echo "3. Enable continuous deployment"
echo "4. Configure custom domain (optional)"