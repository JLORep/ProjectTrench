#!/usr/bin/env python3
"""
Enhanced Unicode Handler for TrenchCoat Pro
Handles all emoji and Unicode issues across Windows console and scripts
"""
import sys
import os
import unicodedata
from typing import Union

class EnhancedUnicodeHandler:
    """Comprehensive Unicode handling for Windows console and files"""
    
    # Safe emoji alternatives (ASCII-compatible)
    EMOJI_FALLBACKS = {
        '🚀': '[ROCKET]',
        '✅': '[OK]',
        '❌': '[FAIL]',
        '⚠️': '[WARN]',
        '🔍': '[SEARCH]',
        '📊': '[CHART]',
        '🎉': '[PARTY]',
        '💥': '[BOOM]',
        '⏰': '[CLOCK]',
        '🔄': '[REFRESH]',
        '📡': '[SIGNAL]',
        '💎': '[GEM]',
        '🟢': '[GREEN]',
        '🔴': '[RED]',
        '🟡': '[YELLOW]',
        '🟠': '[ORANGE]',
        '⭐': '[STAR]',
        '🚨': '[ALERT]',
        '💰': '[MONEY]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '🎯': '[TARGET]',
        '🔥': '[FIRE]',
        '⚡': '[ZAP]',
        '🛡️': '[SHIELD]',
        '🗄️': '[DATABASE]',
        '🎮': '[GAME]',
        '🎭': '[MASK]',
        '🎨': '[ART]',
        '🎪': '[CIRCUS]',
        '🎲': '[DICE]'
    }
    
    def __init__(self, use_fallbacks: bool = None):
        """Initialize Unicode handler
        
        Args:
            use_fallbacks: If True, always use ASCII fallbacks. If None, auto-detect.
        """
        self.use_fallbacks = use_fallbacks
        if use_fallbacks is None:
            self.use_fallbacks = self._should_use_fallbacks()
        
        # Configure console encoding
        self._configure_console()
    
    def _should_use_fallbacks(self) -> bool:
        """Auto-detect if we should use emoji fallbacks"""
        # Check if we're on Windows
        if os.name != 'nt':
            return False
        
        # Check if console supports Unicode
        try:
            # Try to encode a simple emoji
            test_emoji = '✅'
            sys.stdout.buffer.write(test_emoji.encode('cp1252'))
            return False  # If no error, we can use emojis
        except (UnicodeEncodeError, AttributeError):
            return True  # Use fallbacks on encoding errors
    
    def _configure_console(self):
        """Configure console for best Unicode support"""
        try:
            # Try to set UTF-8 encoding
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                
            # Set environment variables for UTF-8
            os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
            
        except Exception:
            # If reconfigure fails, we'll rely on fallbacks
            self.use_fallbacks = True
    
    def safe_text(self, text: str) -> str:
        """Convert text to safe console-compatible format"""
        if not self.use_fallbacks:
            return text
        
        # Replace emojis with fallbacks
        safe_text = text
        for emoji, fallback in self.EMOJI_FALLBACKS.items():
            safe_text = safe_text.replace(emoji, fallback)
        
        # Remove any remaining problematic Unicode characters
        safe_text = unicodedata.normalize('NFKD', safe_text)
        safe_text = safe_text.encode('ascii', errors='replace').decode('ascii')
        
        return safe_text
    
    def safe_print(self, *args, **kwargs):
        """Safe print function that handles Unicode properly"""
        # Convert all arguments to safe text
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(self.safe_text(arg))
            else:
                safe_args.append(str(arg))
        
        try:
            print(*safe_args, **kwargs)
        except UnicodeEncodeError:
            # Final fallback - convert everything to ASCII
            ascii_args = []
            for arg in safe_args:
                ascii_arg = arg.encode('ascii', errors='replace').decode('ascii')
                ascii_args.append(ascii_arg)
            print(*ascii_args, **kwargs)
    
    def safe_write_file(self, filepath: str, content: str, encoding: str = 'utf-8'):
        """Safely write content to file with proper encoding"""
        try:
            with open(filepath, 'w', encoding=encoding, errors='replace') as f:
                f.write(content)
            return True
        except Exception as e:
            # Fallback to ASCII
            try:
                safe_content = self.safe_text(content)
                with open(filepath, 'w', encoding='ascii', errors='replace') as f:
                    f.write(safe_content)
                return True
            except Exception:
                return False
    
    def is_unicode_safe(self, text: str) -> bool:
        """Check if text can be safely displayed in current console"""
        try:
            if os.name == 'nt':
                text.encode('cp1252')
            else:
                text.encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False

# Global instance
unicode_handler = EnhancedUnicodeHandler()

# Convenience functions
def safe_print(*args, **kwargs):
    """Global safe print function"""
    unicode_handler.safe_print(*args, **kwargs)

def safe_text(text: str) -> str:
    """Global safe text conversion"""
    return unicode_handler.safe_text(text)

def configure_unicode_environment():
    """Configure the entire environment for Unicode support"""
    try:
        # Set process-wide encoding
        if hasattr(sys, 'stdout') and hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys, 'stderr') and hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        
        # Environment variables
        os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
        os.environ['PYTHONUTF8'] = '1'
        
        return True
    except Exception:
        return False

# Auto-configure on import
configure_unicode_environment()

if __name__ == "__main__":
    # Test the handler
    handler = EnhancedUnicodeHandler()
    
    print("Testing Unicode Handler:")
    test_strings = [
        "🚀 Starting deployment...",
        "✅ Success!",
        "❌ Failed!",
        "⚠️ Warning message",
        "📊 Analytics data",
        "🎉 Celebration time!"
    ]
    
    for test_str in test_strings:
        print(f"Original: {repr(test_str)}")
        print(f"Safe:     {handler.safe_text(test_str)}")
        handler.safe_print(f"Print:    {test_str}")
        print("-" * 40)