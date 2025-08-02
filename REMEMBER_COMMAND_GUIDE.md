# /remember - Crash Recovery Command

## Overview
The `/remember` command provides comprehensive context recovery after Claude Code crashes or sessions end. It scans all documentation, recent git activity, and system state to resume work exactly where you left off.

## Usage

### Basic Usage
```bash
/remember
```
Outputs a human-readable summary of current context.

### Advanced Usage
```bash
/remember --json                    # Output raw JSON data
/remember --save context.md         # Save analysis to file
/remember --json --save data.json   # Save JSON analysis
```

## What It Analyzes

### 🌿 Git Activity
- Current branch and status
- Last 10 commits with details
- Modified/untracked files
- Repository health

### 📚 Documentation Priority
Files are prioritized by relevance:
1. **Critical**: `CLAUDE.md`, `CLAUDE_QUICK_CONTEXT.md`, `GOTCHAS_AND_LESSONS_LEARNED.md`
2. **Session Files**: Recent session summaries and today's work
3. **Bug Fixes**: Any files containing 'fix', 'bug', 'error', 'gotcha'
4. **Architecture**: Guides, protocols, architecture docs
5. **Deployment**: Production and deployment related files

### 📋 Recent Activity
- Log files from last 24 hours
- Console output and error logs
- Deployment validation files
- System health checks

### 🗄️ Database Status
- Coin count and database size
- Database accessibility
- Data integrity checks

### 💻 System Environment
- Working directory
- Python version
- Environment variables
- Platform information

## Output Example

```
🔄 **CRASH RECOVERY CONTEXT**
Generated: 2025-08-02 21:50:36

🌿 **Current Branch**: main
📊 **Git Status**: Modified files detected

📝 **Recent Commits**:
  • 80aa64e SECURITY: Implement Paranoid Security System
  • 2dff320 FIX: Dashboard bugs - blog system AttributeError
  • ab062ef DOCS: Consolidated all gotchas into single file

🗄️ **Database**: 1733 coins (752KB)

📚 **Key Documentation** (most relevant):
  • CLAUDE.md (modified: 08-02 21:10)
  • GOTCHAS_AND_LESSONS_LEARNED.md (modified: 08-02 21:10)
  • SESSION_SUMMARY_2025_07_31.md (modified: 08-02 16:59)

📋 **Recent Logs**:
  • deployment_validation.json (modified: 08-02 21:28)
  • git_hygiene.log (modified: 08-02 19:57)

💻 **Environment**: C:\Trench
🐍 **Python**: 3.11.9
```

## Integration with Claude Code

The command is designed to provide maximum context with minimal reading time:

1. **Quick Scan**: Essential info in first few lines
2. **Prioritized Content**: Most relevant files listed first  
3. **Timestamp Awareness**: Shows when files were last modified
4. **Status Indicators**: Clear visual cues for system health

## Best Practices

### After a Crash
1. Run `/remember` immediately
2. Review the output to understand current state
3. Check git status for uncommitted work
4. Verify database integrity
5. Review recent documentation changes

### For Handoffs
```bash
/remember --save handoff_context.md
```
Creates a comprehensive handoff document.

### For Debugging
```bash
/remember --json --save debug_context.json
```
Saves raw data for detailed analysis.

## Files Created

- `remember_command.py` - Main command implementation
- `slash_commands/remember.py` - Claude Code integration
- `REMEMBER_COMMAND_GUIDE.md` - This documentation

## Technical Details

### File Priority Algorithm
- Scans modification times and file names
- Weights by criticality and recent activity
- Prioritizes session summaries and gotcha files
- Includes deployment and bug fix documentation

### Performance
- Fast scan of all MD files
- Efficient git log parsing
- Minimal system resource usage
- Concurrent file analysis where possible

### Error Handling
- Graceful handling of missing files
- Fallback for git access issues
- Safe handling of corrupted logs
- Detailed error reporting in JSON mode

---

*Created: 2025-08-02 - Part of TrenchCoat Pro development tools*