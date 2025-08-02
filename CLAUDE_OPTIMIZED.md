# TrenchCoat Pro - Optimized Project Context

> **Quick Start**: See `CLAUDE_QUICK_CONTEXT.md` for 2KB instant recovery

## Project Overview
**TrenchCoat Pro** - Ultra-premium cryptocurrency trading intelligence platform  
- **Live**: https://trenchdemo.streamlit.app
- **GitHub**: https://github.com/JLORep/ProjectTrench
- **Scale**: 851 Python files, 1,733 coins in database
- **Stack**: Python 3.11.9, Streamlit 1.32.0, SQLite

## Navigation Structure
```
CLAUDE_QUICK_CONTEXT.md (2KB)  <- START HERE FOR FAST RECOVERY
├── CLAUDE_OPTIMIZED.md (This file - 10KB essential info)
├── CLAUDE_SESSIONS.md (Detailed session history)
├── CLAUDE_ARCHITECTURE.md (Technical implementation)
└── CLAUDE_PROTOCOLS.md (Development rules)
```

## Current Production Status (2025-08-02)

### Active Features
| Feature | Status | Location |
|---------|---------|----------|
| 12-Tab Dashboard | ✅ Live | `streamlit_app.py` |
| Clickable Coin Cards | ✅ Active | Tab 2 - Lines 1033-1459 |
| Discord Queue System | ✅ Running | `comprehensive_dev_blog_system.py` |
| Auto Library Updates | ✅ Integrated | `enhanced_auto_library_updater.py` |
| Hunt Hub Scanner | ✅ Active | Tab 3 - `hunt_hub_scanner.py` |
| Alpha Radar | ✅ Active | Tab 4 - `alpha_radar_system.py` |

### Latest Deployments
- **2025-08-02 16:19**: Documentation update (b9cded3e)
- **2025-08-02 16:18**: Library updater integration (dcb67b8e)
- **2025-08-02 16:14**: Requirements.txt added (80edaca5)
- **2025-08-02 16:09**: Discord Queue Monitor (641a5a7c)
- **2025-08-02 15:48**: Rate limit queue system (f88e9f4)

## Critical System Components

### 1. Dashboard Architecture (streamlit_app.py)
```python
# Tab structure starts at line 854
tab1, tab2, ..., tab12 = st.tabs([...])

# Key features:
- Coin cards: show_detailed_coin_view() at line 141
- Hunt Hub: Lines 1261-1352
- Alpha Radar: Lines 1354-1445
- Blog + Queue Monitor: Lines 2075-2157
```

### 2. Essential Files
```
streamlit_app.py              # Main dashboard (2300+ lines)
requirements.txt              # Dependencies (incl. aiohttp)
data/trench.db               # Database - DO NOT DELETE
comprehensive_dev_blog_system.py  # Discord integration
enhanced_auto_library_updater.py  # Safe updates
safe_file_editor.py          # Unicode-safe editing
```

### 3. API Integration (17 Sources)
- DexScreener, Jupiter, CoinGecko, Birdeye
- Raydium, Orca, Solscan, Helius
- Full list in `unified_api_integration_layer.py`

## Key Innovations

### 1. Clickable Coin Cards
- Entire card clickable (no small buttons)
- Full detailed view with 5 tabs
- Charts and AI recommendations
- Implementation: `show_detailed_coin_view()`

### 2. Discord Queue System
- Handles 30 req/channel/60s rate limit
- Priority queuing (CRITICAL > HIGH > NORMAL > LOW)
- Automatic retry with backoff
- Monitor in Blog tab

### 3. Auto Library Updater
- Pre/post update validation
- Conservative updates for critical libs
- Automatic rollback on failure
- Integrates with deployment pipeline

## Quick Recovery Procedures

### After Crash/Power Cut
```bash
# 1. Check git status
git status

# 2. Verify database
python -c "import sqlite3; print(sqlite3.connect('data/trench.db').execute('SELECT COUNT(*) FROM coins').fetchone())"

# 3. Test app loads
streamlit run streamlit_app.py

# 4. If issues, check logs
cat complete_async_deploy.log
```

### Common Fixes
| Issue | Solution |
|-------|----------|
| Unicode errors | `python fix_unicode_system.py` |
| Git corruption | `python prevent_git_corruption.py` |
| Missing deps | `pip install -r requirements.txt` |
| Import errors | Check comprehensive_dev_blog_system needs aiohttp |

## Development Workflow

### 1. Making Changes
```bash
# Use safe editor to prevent errors
python safe_file_editor.py

# Or use enhanced library updater
python enhanced_auto_library_updater.py --check-updates
```

### 2. Deployment
```bash
# Auto-deploy pipeline
git add -A
git commit -m "Description"
git push  # Triggers auto-deploy

# Manual validation
python enhanced_deployment_validator.py
```

### 3. Documentation
```bash
# Update all docs after changes
python update_all_docs.py "Session Title" "Description"
```

## Session Highlights

### 2025-08-02 Achievements
1. **Clickable Coin Cards** - Complete UI overhaul
2. **Discord Queue System** - 30k credits of work preserved
3. **Library Update System** - Automated with validation
4. **Documentation System** - 43 files auto-updated
5. **Requirements.txt** - All dependencies documented

### Critical Learnings
- Always check existing files before creating new ones
- Use `comprehensive_dev_blog_system.py` - already built
- Streamlit tab context: Use if/else for exclusive rendering
- Unicode fixes: Permanent solution in place
- Validation: Always run before deploy

## Next Priority: CLAUDE.md Optimization
Original: 49KB with massive duplication  
This file: 10KB essential information  
Quick Context: 2KB for instant recovery

---
*See CLAUDE_SESSIONS.md for complete history*