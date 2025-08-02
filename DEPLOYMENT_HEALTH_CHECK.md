# TrenchCoat Pro - Deployment Health Check Guide

## 🚨 When Deployment Doesn't Show Changes

### Quick Checks:
1. **Verify GitHub Push**:
   ```bash
   git log --oneline -1
   git status
   ```

2. **Force Streamlit Rebuild**:
   - Update DEPLOYMENT_TIMESTAMP in streamlit_app.py
   - Commit and push

3. **Check Streamlit Cloud Dashboard**:
   - Go to https://share.streamlit.io
   - Look for build logs
   - Check for error messages

### Common Issues:

#### 1. **Import Errors**
- Missing requirements.txt entries
- Module not found errors
- Version conflicts

#### 2. **Database Issues**
- SQLite file not found
- Path issues on cloud vs local

#### 3. **Memory/Resource Limits**
- App too large
- Too many imports
- Large data files

### Debug Steps:

1. **Create Minimal Test**:
```python
import streamlit as st
st.title("Test Deploy")
st.write("If you see this, basic deploy works")
```

2. **Check Requirements**:
```bash
pip freeze > requirements_check.txt
# Compare with requirements.txt
```

3. **Test Locally**:
```bash
streamlit run streamlit_app.py
```

4. **Monitor Logs**:
- Streamlit Cloud logs
- GitHub Actions logs
- Post-commit hook output

### Verification Script Usage:
```bash
python verify_deployment.py
```

This checks:
- HTTP response
- Key content presence
- Tab structure
- Error messages

### If All Else Fails:
1. Reboot app on Streamlit Cloud
2. Clear cache and redeploy
3. Check Streamlit status page
4. Try alternate deployment branch