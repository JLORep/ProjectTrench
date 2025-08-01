# 🚀 Azure Manual Deployment Guide

## 🎯 **QUICK AZURE DEPLOYMENT:**

### **Step 1: Go to Azure Portal**
**URL:** https://portal.azure.com
**Login:** Use your existing Azure account

### **Step 2: Create Resource Group**
1. **Search:** "Resource groups"
2. **Click:** "Create"
3. **Name:** `trenchcoat-pro`
4. **Region:** `East US`
5. **Click:** "Review + create"

### **Step 3: Create App Service**
1. **Search:** "App Service"
2. **Click:** "Create" → "Web App"
3. **Fill in:**
   ```
   Resource Group: trenchcoat-pro
   Name: trenchcoat-pro
   Runtime stack: Python 3.11
   Operating System: Linux
   Region: East US
   ```
4. **Pricing Plan:**
   - **Click:** "Change size"
   - **Select:** "Basic B1" ($13.14/month)
   - **Click:** "Apply"

### **Step 4: Deploy Code**
1. **After creation:** Go to your new App Service
2. **Left menu:** "Deployment Center"
3. **Source:** "Local Git" or "ZIP Deploy"
4. **Upload:** `azure_deployment.zip` (already created)

### **Step 5: Configure Custom Domain**
1. **Left menu:** "Custom domains"
2. **Click:** "Add custom domain"
3. **Domain:** `app.trenchcoat.pro`
4. **Follow validation steps**

### **Step 6: SSL Certificate**
1. **Left menu:** "TLS/SSL settings"
2. **Click:** "Add TLS/SSL binding"
3. **Select:** "Free App Service Managed Certificate"

## 📦 **DEPLOYMENT FILES READY:**
- ✅ `azure_deployment.zip` - Contains all app files
- ✅ `streamlit_app.py` - Main application
- ✅ `requirements.txt` - Dependencies
- ✅ All dashboard components

## ⏰ **ESTIMATED TIME:**
- **Resource creation:** 5 minutes
- **App deployment:** 10 minutes
- **Domain setup:** 5 minutes
- **SSL configuration:** 5 minutes
- **Total:** ~25 minutes

## 🎯 **RESULT:**
**Your production URL:** `https://app.trenchcoat.pro`

**Ready to start? Go to:** https://portal.azure.com