# 🌐 TrenchCoat Pro - Subdomain Architecture

## 🎯 **MASTER DOMAIN STRUCTURE:**

### **Primary Domain**: `trenchcoat.pro`

```
trenchcoat.pro/
├── app.trenchcoat.pro          (Main Dashboard - Production)
├── demo.trenchcoat.pro         (Public Demo - Streamlit)
├── api.trenchcoat.pro          (API Endpoints)
├── docs.trenchcoat.pro         (Documentation)
├── blog.trenchcoat.pro         (Content Marketing)
├── status.trenchcoat.pro       (System Status)
└── admin.trenchcoat.pro        (Admin Panel)
```

## 🚀 **DEPLOYMENT MAPPING:**

### **Production Stack:**
- **Main Site**: `https://trenchcoat.pro` → Landing page
- **App**: `https://app.trenchcoat.pro` → Azure App Service (Production)
- **Demo**: `https://demo.trenchcoat.pro` → Streamlit Cloud (UAT)

### **Development Stack:**
- **Staging**: `https://staging.trenchcoat.pro` → Azure (Staging slot)
- **Dev**: `https://dev.trenchcoat.pro` → Development environment
- **Test**: `https://test.trenchcoat.pro` → Testing environment

## 📊 **FUNCTIONAL SUBDOMAINS:**

### **User-Facing:**
- `app` - Main dashboard (authenticated users)
- `demo` - Public demo (no login required)
- `www` - Marketing website (redirects to main)

### **Technical:**
- `api` - REST API endpoints
- `ws` - WebSocket connections
- `cdn` - Static assets and media

### **Business:**
- `blog` - Content marketing and SEO
- `docs` - User guides and API documentation
- `status` - Uptime and system status
- `support` - Help desk and tickets

### **Internal:**
- `admin` - Administrative dashboard
- `monitor` - Monitoring and analytics
- `backup` - Backup and recovery systems

## 🔐 **SECURITY & SSL:**

### **SSL Certificate Strategy:**
- **Wildcard SSL**: `*.trenchcoat.pro` (covers all subdomains)
- **Provider**: Azure App Service SSL (free) or Cloudflare
- **Auto-renewal**: Enabled for all certificates

### **Security Headers:**
```
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

## 📱 **URL Examples:**

### **Main Application:**
```
https://app.trenchcoat.pro/dashboard
https://app.trenchcoat.pro/settings
https://app.trenchcoat.pro/analytics
```

### **API Endpoints:**
```
https://api.trenchcoat.pro/v1/coins
https://api.trenchcoat.pro/v1/strategies
https://api.trenchcoat.pro/v1/performance
```

### **Documentation:**
```
https://docs.trenchcoat.pro/getting-started
https://docs.trenchcoat.pro/api-reference
https://docs.trenchcoat.pro/tutorials
```

## 🎯 **DNS CONFIGURATION:**

### **Required DNS Records:**
```
A       trenchcoat.pro          → Azure IP
CNAME   app                     → trenchcoat-pro.azurewebsites.net
CNAME   demo                    → projecttrench-uat.streamlit.app
CNAME   api                     → trenchcoat-api.azurewebsites.net
CNAME   docs                    → trenchcoat-docs.github.io
CNAME   blog                    → trenchcoat-blog.ghost.io
```

### **Email Configuration:**
```
MX      trenchcoat.pro          → Google Workspace / Outlook
CNAME   mail                    → mail.google.com
TXT     @                       → SPF/DKIM records
```

## 🚀 **IMPLEMENTATION PRIORITY:**

### **Phase 1 (Immediate):**
1. **Register**: `trenchcoat.pro`
2. **Set up**: `app.trenchcoat.pro` → Azure
3. **Configure**: `demo.trenchcoat.pro` → Streamlit

### **Phase 2 (Next Week):**
4. **Add**: `api.trenchcoat.pro` → API services
5. **Create**: `docs.trenchcoat.pro` → GitHub Pages
6. **Launch**: `blog.trenchcoat.pro` → Content marketing

### **Phase 3 (Next Month):**
7. **Deploy**: `status.trenchcoat.pro` → Status page
8. **Setup**: `admin.trenchcoat.pro` → Admin panel
9. **Configure**: Email and support systems

## 💰 **COST ESTIMATION:**

### **Domain Costs:**
- `trenchcoat.pro`: $25/year
- Wildcard SSL: FREE (via Azure)
- DNS hosting: FREE (Azure DNS)

### **Hosting Costs:**
- Azure App Service: $13-50/month
- Streamlit Cloud: FREE
- Total estimated: $15-55/month

## ✅ **SUBDOMAIN ARCHITECTURE COMPLETE**

**Ready for domain registration and DNS setup!**