# 🧹 Git Hygiene System

## Overview

The Git Hygiene System provides automated, safe garbage collection and repository maintenance to prevent corruption errors and maintain optimal performance.

## Features

### 🛡️ Safety Features
- **Automatic Backups**: Creates backup before any maintenance
- **Corrupted Object Detection**: Identifies and removes corrupted git objects
- **Safe GC Options**: Uses conservative garbage collection settings
- **State Tracking**: Maintains history of all maintenance operations

### ♻️ Maintenance Operations
1. **Repository Health Check**
   - Detects corrupted objects
   - Monitors repository size
   - Counts loose objects

2. **Safe Garbage Collection**
   - Prunes old unreachable objects (>2 weeks)
   - Repacks repository with safe options
   - Cleans reflog (>30 days)
   - Performs aggressive GC when needed

3. **Backup Management**
   - Creates timestamped backups
   - Auto-cleans backups older than 7 days
   - Uses fast robocopy on Windows

## Usage

### Manual Run
```bash
# Check repository health
python git_hygiene_manager.py --check-only

# Run full hygiene (if needed)
python git_hygiene_manager.py

# Force immediate cleanup
python git_hygiene_manager.py --force
```

### Automatic Schedule
```bash
# Set up weekly schedule (Windows)
setup_git_hygiene_schedule.bat

# The system will run:
- Full hygiene: Every Sunday at 2:00 AM
- Health check: On system startup
- Quick check: After git pulls/merges
```

## Integration

### Git Hooks
- **Pre-commit**: Disables auto GC to prevent errors
- **Post-commit**: Suppresses GC errors
- **Post-merge**: Runs health check after pulls

### Error Prevention
The system permanently fixes the git gc errors by:
1. Disabling automatic garbage collection (`gc.auto = 0`)
2. Running controlled, safe GC operations periodically
3. Removing corrupted objects before they cause issues
4. Maintaining backups for recovery

## Benefits

✅ **No more gc errors** during commits
✅ **Optimal performance** with regular maintenance  
✅ **Automatic recovery** from corrupted objects
✅ **Peace of mind** with automated backups
✅ **Clean repository** with controlled cleanup

## State File

The system maintains state in `.git_hygiene_state.json`:
```json
{
  "last_gc": "2025-08-02T19:57:24",
  "gc_count": 1,
  "last_backup": "2025-08-02T19:57:24", 
  "errors_fixed": 3
}
```

## Logs

All operations are logged to `git_hygiene.log` for troubleshooting.

---

*The Git Hygiene System ensures your repository stays healthy and error-free!*