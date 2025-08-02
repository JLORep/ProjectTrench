#\!/usr/bin/env python3
"""
Unicode-safe print handler for Windows
"""
import sys

def safe_print(*args, **kwargs):
    """Safe print function that handles Unicode issues on Windows"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback for Windows console issues
        message = ' '.join(str(arg) for arg in args)
        # Remove problematic Unicode characters
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        print(safe_message, **kwargs)
    except Exception as e:
        # Last resort - just print basic info
        print(f'Print error: {e}')
