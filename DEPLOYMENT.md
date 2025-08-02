# 🚀 TrenchCoat Pro - Deployment Guide

## Quick Start

To deploy TrenchCoat Pro, use the single unified deployment script:

```bash
python deploy.py
```

## Deployment Options

### Full Deployment (Recommended)
```bash
python deploy.py
```
- Runs all pre-deployment checks
- Commits and pushes to GitHub
- Validates deployment
- Sends Discord notifications

### Quick Deployment (No Validation)
```bash
python deploy.py --quick
```
- Skips validation and notifications
- Use only when confident in changes

### Custom Options
```bash
python deploy.py --no-validate  # Skip validation only
python deploy.py --no-notify    # Skip notifications only
```

## How It Works

1. **Pre-deployment Checks**
   - Verifies `streamlit_app.py` exists
   - Confirms database `data/trench.db` is present
   - Checks git repository status

2. **Git Operations**
   - Commits any uncommitted changes
   - Pushes to GitHub main branch
   - Triggers Streamlit Cloud webhook

3. **Streamlit Cloud Deployment**
   - Automatic deployment on push to main
   - Usually takes 60-90 seconds
   - No manual intervention needed

4. **Post-deployment Validation**
   - Waits 60 seconds for deployment
   - Checks if app is accessible
   - Verifies key content is present

5. **Notifications**
   - Sends Discord webhook on success/failure
   - Includes deployment time and URL

## Troubleshooting

### Deployment Failed
1. Check `git status` for uncommitted changes
2. Verify database file exists: `ls data/trench.db`
3. Ensure you're on main branch: `git branch`
4. Check Streamlit Cloud dashboard for errors

### App Not Loading
1. Wait 2-3 minutes for Streamlit to build
2. Check https://share.streamlit.io for build logs
3. Verify `requirements.txt` has all dependencies
4. Ensure no syntax errors in `streamlit_app.py`

### Validation Failed
1. App may still be building - wait and retry
2. Check if URL has changed
3. Verify internet connectivity
4. Manual check: https://trenchdemo.streamlit.app

## Environment Variables

Create `.streamlit/secrets.toml` for sensitive data:
```toml
[discord]
webhook_url = "your_webhook_url_here"

[api_keys]
dexscreener = "your_key_here"
```

## Best Practices

1. **Always test locally first**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Keep database in sync**
   - Never add `data/trench.db` to `.gitignore`
   - Commit database changes separately

3. **Monitor deployments**
   - Check Discord for notifications
   - Verify app functionality after deploy

4. **Use meaningful commit messages**
   - Deployment script auto-generates timestamps
   - Add context in manual commits

## Emergency Rollback

If deployment breaks production:
```bash
git reset --hard HEAD~1
git push --force origin main
```

This will revert to the previous working version.

## Support

- Streamlit Cloud Dashboard: https://share.streamlit.io
- GitHub Repo: https://github.com/JLORep/ProjectTrench
- Discord Notifications: Check #deployments channel

---

*Last updated: 2025-08-02 - Simplified from 28+ scripts to 1*