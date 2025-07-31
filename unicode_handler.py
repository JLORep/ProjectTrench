#!/usr/bin/env python3
"""
TrenchCoat Pro - Unicode & Emoji Handler
Prevents encoding errors across all scripts on Windows
"""
import sys
import os
import codecs
from typing import Optional, Dict, Any

class UnicodeHandler:
    """Handles Unicode and emoji output safely across platforms"""
    
    # Emoji mappings for fallback
    EMOJI_FALLBACKS = {
        '✅': '[SUCCESS]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🚀': '[DEPLOY]',
        '🎯': '[TARGET]',
        '📊': '[DATA]',
        '💎': '[PREMIUM]',
        '🔧': '[CONFIG]',
        '📝': '[LOG]',
        '🔒': '[LOCK]',
        '⏰': '[TIME]',
        '🔔': '[NOTIFY]',
        '🛡️': '[SECURE]',
        '⚡': '[FAST]',
        '🟢': '[ONLINE]',
        '🔴': '[OFFLINE]',
        '🟡': '[PENDING]',
        '🔵': '[INFO]',
        '🚨': '[ALERT]',
        '📡': '[LIVE]',
        '💰': '[MONEY]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '🎪': '[CONFIDENCE]',
        '💧': '[LIQUIDITY]',
        '🚫': '[BLOCKED]',
        '💥': '[CRASH]',
        '🕐': '[TIMEOUT]',
        '🤖': '[BOT]',
        '🔄': '[REFRESH]',
        '🔗': '[LINK]',
        '⏱️': '[TIMER]',
        '🆕': '[NEW]',
        '🏆': '[WIN]',
        '📋': '[LIST]',
        '🎮': '[GAME]',
        '🌟': '[STAR]',
        '💻': '[TECH]',
        '🔮': '[PREDICT]',
        '🎨': '[DESIGN]',
        '📱': '[MOBILE]',
        '🌐': '[WEB]',
        '🔐': '[AUTH]',
        '📞': '[CALL]',
        '✨': '[MAGIC]',
        '🎭': '[MASK]',
        '🎲': '[RANDOM]',
        '🔍': '[SEARCH]',
        '🗄️': '[DATABASE]',
        '🧠': '[AI]',
        '🎛️': '[CONTROL]',
        '📦': '[PACKAGE]',
        '🌈': '[RAINBOW]',
        '🎊': '[PARTY]',
        '🎉': '[CELEBRATE]',
        '🔊': '[SOUND]',
        '🔇': '[MUTE]',
        '🎵': '[MUSIC]',
        '📺': '[SCREEN]',
        '💡': '[IDEA]',
        '🔥': '[HOT]',
        '❄️': '[COLD]',
        '⭐': '[FAVORITE]',
        '💪': '[STRONG]',
        '🚪': '[DOOR]',
        '🔑': '[KEY]',
        '🗝️': '[OLDKEY]',
        '🔓': '[UNLOCK]',
        '⚙️': '[GEAR]',
        '🔨': '[HAMMER]',
        '🪛': '[SCREWDRIVER]',
        '🧰': '[TOOLBOX]',
        '⚡️': '[ELECTRIC]',
        '💼': '[BUSINESS]',
        '👔': '[FORMAL]',
        '🎩': '[HAT]',
        '👑': '[CROWN]',
        '💍': '[RING]',
        '💎': '[DIAMOND]',
        '🏅': '[MEDAL]',
        '🏆': '[TROPHY]'
    }
    
    def __init__(self):
        self.platform = sys.platform
        self.encoding = self._get_best_encoding()
        self.setup_console()
    
    def _get_best_encoding(self) -> str:
        """Determine the best encoding for the current platform"""
        if self.platform == 'win32':
            # Try to use UTF-8 on Windows
            try:
                # Test if we can encode/decode properly
                test_text = "🚀 Test Unicode"
                test_text.encode('utf-8').decode('utf-8')
                return 'utf-8'
            except (UnicodeEncodeError, UnicodeDecodeError):
                return 'cp1252'  # Windows fallback
        else:
            return 'utf-8'  # Unix systems
    
    def setup_console(self):
        """Setup console for proper Unicode output"""
        if self.platform == 'win32':
            try:
                # Try to set console to UTF-8 mode
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleCP(65001)  # UTF-8
                kernel32.SetConsoleOutputCP(65001)  # UTF-8
                
                # Reconfigure stdout/stderr
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                    
                self.encoding = 'utf-8'
                self.unicode_supported = True
                
            except (ImportError, AttributeError, OSError):
                # Fallback to ASCII-safe mode
                self.unicode_supported = False
        else:
            self.unicode_supported = True
    
    def safe_print(self, text: str, **kwargs):
        """Print text safely, handling Unicode errors"""
        try:
            if self.unicode_supported:
                print(text, **kwargs)
            else:
                # Replace emojis with fallback text
                safe_text = self.replace_emojis(text)
                print(safe_text, **kwargs)
                
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Final fallback - replace all non-ASCII
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            safe_text = self.replace_emojis(safe_text)
            print(safe_text, **kwargs)
    
    def replace_emojis(self, text: str) -> str:
        """Replace emojis with ASCII-safe alternatives"""
        for emoji, fallback in self.EMOJI_FALLBACKS.items():
            text = text.replace(emoji, fallback)
        return text
    
    def safe_format(self, template: str, **kwargs) -> str:
        """Safely format strings with Unicode content"""
        try:
            formatted = template.format(**kwargs)
            if not self.unicode_supported:
                formatted = self.replace_emojis(formatted)
            return formatted
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Replace emojis and try again
            safe_template = self.replace_emojis(template)
            return safe_template.format(**kwargs)
    
    def write_safe_file(self, filepath: str, content: str, encoding: Optional[str] = None):
        """Write file with safe Unicode handling"""
        if encoding is None:
            encoding = self.encoding
            
        try:
            with open(filepath, 'w', encoding=encoding, errors='replace') as f:
                f.write(content)
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback to ASCII-safe content
            safe_content = self.replace_emojis(content)
            with open(filepath, 'w', encoding='ascii', errors='replace') as f:
                f.write(safe_content)
    
    def read_safe_file(self, filepath: str, encoding: Optional[str] = None) -> str:
        """Read file with safe Unicode handling"""
        if encoding is None:
            encoding = self.encoding
            
        try:
            with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            # Try with different encodings
            for fallback_encoding in ['utf-8', 'cp1252', 'latin1']:
                try:
                    with open(filepath, 'r', encoding=fallback_encoding, errors='replace') as f:
                        return f.read()
                except (UnicodeDecodeError, FileNotFoundError):
                    continue
            raise

# Global instance
unicode_handler = UnicodeHandler()

# Convenience functions
def safe_print(text: str, **kwargs):
    """Global safe print function"""
    unicode_handler.safe_print(text, **kwargs)

def safe_format(template: str, **kwargs) -> str:
    """Global safe format function"""
    return unicode_handler.safe_format(template, **kwargs)

def replace_emojis(text: str) -> str:
    """Global emoji replacement function"""
    return unicode_handler.replace_emojis(text)

def write_safe_file(filepath: str, content: str, encoding: Optional[str] = None):
    """Global safe file write function"""
    unicode_handler.write_safe_file(filepath, content, encoding)

def read_safe_file(filepath: str, encoding: Optional[str] = None) -> str:
    """Global safe file read function"""
    return unicode_handler.read_safe_file(filepath, encoding)

# Decorators for automatic handling
def unicode_safe(func):
    """Decorator to make functions Unicode-safe"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            safe_print(f"[UNICODE ERROR] Function {func.__name__}: {e}")
            # Try to call with ASCII-safe arguments
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    safe_args.append(replace_emojis(arg))
                else:
                    safe_args.append(arg)
            
            safe_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    safe_kwargs[key] = replace_emojis(value)
                else:
                    safe_kwargs[key] = value
            
            return func(*safe_args, **safe_kwargs)
    return wrapper

if __name__ == "__main__":
    # Test the Unicode handler
    print("=" * 50)
    print("Unicode Handler Test")
    print("=" * 50)
    
    test_messages = [
        "✅ Success message with emoji",
        "❌ Error message with emoji", 
        "🚀 Deployment started!",
        "💎 TrenchCoat Pro is running",
        "🔧 Configuration updated",
        "Regular ASCII text without emojis"
    ]
    
    for msg in test_messages:
        safe_print(f"Testing: {msg}")
    
    print("\n" + "=" * 50)
    print("Unicode Handler Test Complete")
    print("=" * 50)