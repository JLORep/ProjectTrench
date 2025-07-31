#!/usr/bin/env python3
"""
TrenchCoat Pro - Async Hook Installer
Installs Python-based async deployment hook
"""
import os
import shutil
import sys
from pathlib import Path
from unicode_handler import safe_print

def create_python_hook():
    """Create Python-based git hook"""
    project_dir = Path.cwd()
    hooks_dir = project_dir / '.git' / 'hooks'
    hook_file = hooks_dir / 'post-commit'
    
    # Python hook content
    hook_content = '''#!/usr/bin/env python3
import subprocess
import sys

# Run the async deployment hook
try:
    result = subprocess.run([
        sys.executable, "async_deployment_hook.py"
    ], timeout=10, cwd=r"''' + str(project_dir) + '''")
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print("Hook timeout - continuing")
    sys.exit(0)
except Exception as e:
    print(f"Hook error: {e}")
    sys.exit(0)
'''
    
    # Backup existing hook
    if hook_file.exists():
        backup_file = hooks_dir / 'post-commit.backup-async'
        shutil.copy2(hook_file, backup_file)
        safe_print(f"✅ Backed up existing hook to {backup_file}")
    
    # Write new hook
    hook_file.write_text(hook_content)
    safe_print(f"✅ Created Python hook: {hook_file}")
    
    # Make executable on Unix
    if os.name != 'nt':
        os.chmod(hook_file, 0o755)
        safe_print("✅ Made hook executable")
    
    return True

def main():
    """Install async hook"""
    safe_print("=" * 60)
    safe_print("🚀 Installing Async Deployment Hook")
    safe_print("=" * 60)
    
    try:
        # Create the hook
        if create_python_hook():
            safe_print("\n✅ ASYNC HOOK INSTALLED SUCCESSFULLY!")
            safe_print("\nFeatures:")
            safe_print("- ⚡ Instant git commits (no timeouts)")
            safe_print("- 🔄 Truly async deployment")
            safe_print("- 🛡️ Error handling and recovery")
            safe_print("- 📝 Comprehensive logging")
            safe_print("\nNext deployment-triggering commit will test the system!")
            return 0
        else:
            safe_print("\n❌ Hook installation failed")
            return 1
            
    except Exception as e:
        safe_print(f"\n❌ Installation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())