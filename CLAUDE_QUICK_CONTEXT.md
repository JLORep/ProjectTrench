# 🚀 TrenchCoat Pro - QUICK CONTEXT RECOVERY

## 🎯 INSTANT PROJECT SUMMARY
**What**: Ultra-premium crypto trading platform with AI intelligence  
**Live**: https://trenchdemo.streamlit.app  
**GitHub**: https://github.com/JLORep/ProjectTrench  
**Database**: 1,733 coins in `data/trench.db` (DO NOT DELETE)  
**Entry**: `streamlit_app.py` (12-tab Streamlit dashboard)

## 🔥 CURRENT STATE (2025-08-02 16:20)
```
✅ Production deployed and running
✅ All 12 tabs functional
✅ Discord queue system active
✅ Auto-deploy pipeline working
✅ Library updater integrated
✅ Requirements.txt updated
```

## 📌 CRITICAL COMMANDS
```bash
# Quick deployment
git add -A && git commit -m "Update" && git push

# Test locally
streamlit run streamlit_app.py

# Check database
python -c "import sqlite3; print(sqlite3.connect('data/trench.db').execute('SELECT COUNT(*) FROM coins').fetchone())"

# Update libraries safely
python enhanced_auto_library_updater.py --run

# Update all docs
python update_all_docs.py "Session Name" "Description"
```

## 🏗️ 12-TAB STRUCTURE
1. **🚀 Dashboard** - Market overview (Tab 1)
2. **💎 Coins** - Database with CLICKABLE CARDS (Tab 2)
3. **🎯 Hunt Hub** - Memecoin sniping (Tab 3)
4. **📡 Alpha Radar** - AI signals (Tab 4)
5. **🛡️ Security** - Threat monitoring (Tab 5)
6. **🔧 Enrichment** - API integration (Tab 6)
7. **🤖 Super Claude** - AI assistant (Tab 7)
8. **📱 Blog** - Dev updates + Queue Monitor (Tab 8)
9. **📊 Monitoring** - System health (Tab 9)
10. **⚙️ System** - Configuration (Tab 10)
11. **🧪 Beta** - Experimental (Tab 11)
12. **🎮 Runners** - Bot automation (Tab 12)

## 🔧 KEY SYSTEMS
- **Discord Queue**: Rate limit management in `comprehensive_dev_blog_system.py`
- **Auto Deploy**: Git hooks trigger Streamlit deployment
- **Library Updates**: Validation-based updates in `enhanced_auto_library_updater.py`
- **Safe Editor**: Unicode-safe file editing in `safe_file_editor.py`
- **API Integration**: 17 sources in `unified_api_integration_layer.py`

## ⚠️ COMMON ISSUES & FIXES

### Unicode Errors
```bash
python fix_unicode_system.py
```

### Git Corruption
```bash
python prevent_git_corruption.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Deployment Failed
```python
# Force rebuild - update timestamp in streamlit_app.py
# Line ~2300: st.markdown(f"<!-- Deployment timestamp: {datetime.now()} -->")
```

## 📦 LATEST FEATURES (2025-08-02)
1. **Clickable Coin Cards** - Full detailed view with charts
2. **Discord Queue System** - No more 429 rate limit errors
3. **Automated Library Updates** - Safe updates with validation
4. **Comprehensive Blog System** - Multi-channel Discord integration
5. **Enhanced Validation** - Pre/post deployment checks

## 🚨 DO NOT DELETE
- `data/trench.db` - Production database
- `requirements.txt` - Dependencies
- `.git/hooks/` - Auto-deploy hooks
- `deployment_validation.json` - Deploy status

## 📚 DETAILED DOCS
- **Sessions**: `CLAUDE_SESSIONS.md` - All work history
- **Architecture**: `CLAUDE_ARCHITECTURE.md` - Technical details
- **Protocols**: `CLAUDE_PROTOCOLS.md` - Rules & practices

## 💡 QUICK WINS
- Always run `update_all_docs.py` after major changes
- Check validation before deploy: `python validate_code.py`
- Use safe editor for file changes: `python safe_file_editor.py`
- Monitor queue in Blog tab > Queue Monitor

---
*For full context, see CLAUDE.md (49KB) - This is the 2KB quick recovery version*