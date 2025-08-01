# Emergency Revert Instructions

## If Streamlit App is Stuck (Spinning Circle)

### Option 1: Reboot on Streamlit Cloud
1. Go to Streamlit Cloud dashboard
2. Click "Manage app" (bottom right of app)
3. Click "Reboot app" 
4. Wait 2-3 minutes for fresh deployment

### Option 2: Revert to Last Working Version
The last known working version before charts integration:
```bash
git revert --no-commit d95509a..HEAD
git commit -m "EMERGENCY: Revert to stable version before charts"
git push
```

### Option 3: Deploy Safe Minimal Version
```bash
# Rename safe version to main app
mv streamlit_app.py streamlit_app_backup.py
mv streamlit_app_safe.py streamlit_app.py
git add -A
git commit -m "EMERGENCY: Deploy safe minimal version"
git push
```

### Last Known Stable Commits:
- `40ef329` - Before chart integration (basic working dashboard)
- `29a22f0` - Stunning coin cards working
- `28909b3` - Database integration working

### To Check Logs:
1. Streamlit Cloud → Manage app → Logs
2. Look for:
   - Import errors
   - Module not found
   - Syntax errors
   - Database connection errors