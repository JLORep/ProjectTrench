# 🌐 TrenchCoat Pro DNS Configuration Guide

## 📍 **CURRENT STATUS:**
You're in the Advanced DNS section - perfect! I can see you already have some records set up.

## 🎯 **REQUIRED DNS RECORDS FOR TRENCHCOAT PRO:**

### **1. Demo Subdomain (Priority 1)**
For your Streamlit demo at `https://demo.trenchcoat.pro`:

```
Type: CNAME Record
Host: demo
Value: projecttrench-uat.streamlit.app
TTL: Automatic (or 30 min)
```

### **2. App Subdomain (For Azure)**
For your main app at `https://app.trenchcoat.pro`:

```
Type: CNAME Record  
Host: app
Value: [Your Azure App Service URL - we'll get this next]
TTL: Automatic
```

### **3. Main Domain Redirect**
For `https://trenchcoat.pro` to redirect to your main app:

```
Type: URL Redirect Record
Host: @
Value: https://app.trenchcoat.pro
TTL: Automatic
```

## 🔧 **HOW TO ADD THE DEMO RECORD:**

### **Step 1: Add CNAME for Demo**
1. **Click**: "ADD NEW RECORD" (red button)
2. **Select**: "CNAME Record" from dropdown
3. **Host**: Enter `demo`
4. **Value**: Enter `projecttrench-uat.streamlit.app`
5. **TTL**: Leave as "Automatic"
6. **Click**: Save/Add

### **Step 2: Test Demo URL**
After 15-30 minutes, test:
`https://demo.trenchcoat.pro`

This should show your ultra-premium dashboard!

## 📊 **WHAT I SEE IN YOUR CURRENT SETUP:**

### **Existing Records:**
- ✅ **CNAME www** → `parkingpage.namecheap.com` (temporary)
- ✅ **URL Redirect @** → `http://www.trenchcoat.pro/` (basic redirect)
- ⚠️ **Need to add**: `demo` CNAME for Streamlit

### **Missing Records (Add These):**
```
demo     CNAME    projecttrench-uat.streamlit.app
app      CNAME    [Azure URL - coming next]
api      CNAME    [API service - future]
```

## 🚀 **IMMEDIATE ACTION:**

**Add this record RIGHT NOW:**

1. **Click**: "ADD NEW RECORD"
2. **Type**: CNAME Record
3. **Host**: `demo`
4. **Value**: `projecttrench-uat.streamlit.app`
5. **Save**

## ⏰ **TIMELINE EXPECTATIONS:**

- **DNS Propagation**: 15-30 minutes
- **SSL Certificate**: Automatic (via Streamlit)
- **Live Demo**: `https://demo.trenchcoat.pro`

## 🎯 **AFTER DEMO IS WORKING:**

Next we'll add:
- `app.trenchcoat.pro` for Azure production
- `api.trenchcoat.pro` for API endpoints
- Professional email MX records

## ✅ **SUCCESS INDICATORS:**

You'll know it worked when:
1. **demo.trenchcoat.pro** loads your dashboard
2. **Professional URL** shows your ultra-premium interface
3. **SSL certificate** is automatically active (🔒)

**Ready to add the demo CNAME record?** This will make your stunning dashboard available at the professional URL! 🚀