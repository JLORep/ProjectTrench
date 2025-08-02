#!/usr/bin/env python3
"""
Enhanced Caching System - Intelligent Multi-Level Caching
Provides smart caching with dependency tracking, automatic invalidation, and performance optimization
"""

import streamlit as st
import time
import hashlib
import json
import pickle
import logging
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
import weakref
from enum import Enum

class CacheLevel(Enum):
    """Cache levels for different data types"""
    MEMORY = "memory"          # In-memory cache (fastest)
    SESSION = "session"        # Streamlit session cache
    DISK = "disk"             # Persistent disk cache
    DISTRIBUTED = "distributed" # Redis/distributed cache (future)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    last_accessed: float = 0
    dependencies: List[str] = None
    cache_level: CacheLevel = CacheLevel.MEMORY
    size_bytes: int = 0
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.last_accessed == 0:
            self.last_accessed = self.created_at

@dataclass 
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    invalidations: int = 0
    total_size: int = 0
    avg_access_time: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

class DependencyTracker:
    """Tracks cache dependencies for intelligent invalidation"""
    
    def __init__(self):
        self.dependencies = {}  # dependency -> set of cache keys
        self.dependents = {}    # cache key -> set of dependencies
        self.lock = threading.Lock()
    
    def add_dependency(self, cache_key: str, dependency: str):
        """Add a dependency relationship"""
        with self.lock:
            if dependency not in self.dependencies:
                self.dependencies[dependency] = set()
            self.dependencies[dependency].add(cache_key)
            
            if cache_key not in self.dependents:
                self.dependents[cache_key] = set()
            self.dependents[cache_key].add(dependency)
    
    def get_dependent_keys(self, dependency: str) -> List[str]:
        """Get all cache keys that depend on a dependency"""
        with self.lock:
            return list(self.dependencies.get(dependency, set()))
    
    def remove_key(self, cache_key: str):
        """Remove a cache key and its dependency relationships"""
        with self.lock:
            if cache_key in self.dependents:
                for dep in self.dependents[cache_key]:
                    if dep in self.dependencies:
                        self.dependencies[dep].discard(cache_key)
                del self.dependents[cache_key]

class EnhancedCacheSystem:
    """
    Multi-level caching system with intelligent features
    """
    
    def __init__(self, 
                 max_memory_size: int = 100 * 1024 * 1024,  # 100MB
                 max_disk_size: int = 500 * 1024 * 1024,    # 500MB
                 cache_dir: str = "data/cache"):
        
        self.max_memory_size = max_memory_size
        self.max_disk_size = max_disk_size
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache storage
        self.memory_cache = {}
        self.disk_cache_index = {}
        
        # Management
        self.dependency_tracker = DependencyTracker()
        self.stats = CacheStats()
        self.lock = threading.Lock()
        
        # Background maintenance
        self._setup_maintenance()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load disk cache index
        self._load_disk_index()
    
    def _setup_maintenance(self):
        """Setup background maintenance thread"""
        def maintenance_worker():
            while True:
                try:
                    time.sleep(300)  # Run every 5 minutes
                    self._cleanup_expired()
                    self._evict_lru_if_needed()
                    self._log_stats()
                except Exception as e:
                    self.logger.error(f"Cache maintenance error: {e}")
        
        maintenance_thread = threading.Thread(target=maintenance_worker, daemon=True)
        maintenance_thread.start()
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key"""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def _get_entry_size(self, value: Any) -> int:
        """Estimate the size of a cache entry"""
        try:
            return len(pickle.dumps(value))
        except:
            return len(str(value).encode('utf-8'))
    
    def _load_disk_index(self):
        """Load disk cache index"""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    self.disk_cache_index = {
                        k: CacheEntry(**v) for k, v in data.items()
                    }
                self.logger.info(f"Loaded {len(self.disk_cache_index)} disk cache entries")
            except Exception as e:
                self.logger.error(f"Failed to load disk cache index: {e}")
    
    def _save_disk_index(self):
        """Save disk cache index"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            data = {
                k: asdict(v) for k, v in self.disk_cache_index.items()
            }
            with open(index_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save disk cache index: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        start_time = time.time()
        
        # Try memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            # Check expiration
            if time.time() > entry.expires_at:
                self._remove_from_memory(key)
                self.stats.misses += 1
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            self.stats.hits += 1
            
            access_time = time.time() - start_time
            self._update_avg_access_time(access_time)
            
            return entry.value
        
        # Try disk cache
        if key in self.disk_cache_index:
            entry = self.disk_cache_index[key]
            
            # Check expiration
            if time.time() > entry.expires_at:
                self._remove_from_disk(key)
                self.stats.misses += 1
                return None
            
            # Load from disk
            cache_file = self.cache_dir / f"{key}.pickle"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        value = pickle.load(f)
                    
                    # Promote to memory cache if frequently accessed
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    
                    if entry.access_count > 3:  # Promote after 3 accesses
                        self._promote_to_memory(key, entry, value)
                    
                    self.stats.hits += 1
                    access_time = time.time() - start_time
                    self._update_avg_access_time(access_time)
                    
                    return value
                    
                except Exception as e:
                    self.logger.error(f"Failed to load cache file {key}: {e}")
                    self._remove_from_disk(key)
        
        self.stats.misses += 1
        return None
    
    def set(self, 
            key: str, 
            value: Any, 
            ttl: int = 3600, 
            dependencies: List[str] = None,
            cache_level: CacheLevel = CacheLevel.MEMORY) -> bool:
        """Set value in cache"""
        
        current_time = time.time()
        expires_at = current_time + ttl
        size_bytes = self._get_entry_size(value)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            expires_at=expires_at,
            dependencies=dependencies or [],
            cache_level=cache_level,
            size_bytes=size_bytes
        )
        
        # Add dependencies
        if dependencies:
            for dep in dependencies:
                self.dependency_tracker.add_dependency(key, dep)
        
        # Store based on cache level
        if cache_level == CacheLevel.MEMORY:
            return self._store_in_memory(key, entry)
        elif cache_level == CacheLevel.DISK:
            return self._store_on_disk(key, entry)
        elif cache_level == CacheLevel.SESSION:
            return self._store_in_session(key, entry)
        
        return False
    
    def _store_in_memory(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in memory cache"""
        with self.lock:
            # Check size limits
            if self._get_memory_size() + entry.size_bytes > self.max_memory_size:
                self._evict_lru_memory()
            
            self.memory_cache[key] = entry
            self.stats.total_size += entry.size_bytes
            return True
    
    def _store_on_disk(self, key: str, entry: CacheEntry) -> bool:
        """Store entry on disk"""
        try:
            cache_file = self.cache_dir / f"{key}.pickle"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(entry.value, f)
            
            # Update index
            entry_copy = CacheEntry(
                key=entry.key,
                value=None,  # Don't store value in index
                created_at=entry.created_at,
                expires_at=entry.expires_at,
                dependencies=entry.dependencies,
                cache_level=entry.cache_level,
                size_bytes=entry.size_bytes
            )
            
            self.disk_cache_index[key] = entry_copy
            self._save_disk_index()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store cache entry on disk: {e}")
            return False
    
    def _store_in_session(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in Streamlit session"""
        try:
            if 'enhanced_cache' not in st.session_state:
                st.session_state.enhanced_cache = {}
            
            st.session_state.enhanced_cache[key] = entry
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store in session cache: {e}")
            return False
    
    def _promote_to_memory(self, key: str, entry: CacheEntry, value: Any):
        """Promote disk cache entry to memory"""
        entry.value = value
        entry.cache_level = CacheLevel.MEMORY
        self._store_in_memory(key, entry)
    
    def invalidate(self, dependencies: Union[str, List[str]]):
        """Invalidate cache entries based on dependencies"""
        if isinstance(dependencies, str):
            dependencies = [dependencies]
        
        keys_to_remove = set()
        
        for dep in dependencies:
            dependent_keys = self.dependency_tracker.get_dependent_keys(dep)
            keys_to_remove.update(dependent_keys)
        
        for key in keys_to_remove:
            self._remove_key(key)
            self.stats.invalidations += 1
        
        if keys_to_remove:
            self.logger.info(f"Invalidated {len(keys_to_remove)} cache entries")
    
    def _remove_key(self, key: str):
        """Remove key from all cache levels"""
        self._remove_from_memory(key)
        self._remove_from_disk(key)
        self._remove_from_session(key)
        self.dependency_tracker.remove_key(key)
    
    def _remove_from_memory(self, key: str):
        """Remove key from memory cache"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            self.stats.total_size -= entry.size_bytes
            del self.memory_cache[key]
    
    def _remove_from_disk(self, key: str):
        """Remove key from disk cache"""
        if key in self.disk_cache_index:
            cache_file = self.cache_dir / f"{key}.pickle"
            if cache_file.exists():
                cache_file.unlink()
            del self.disk_cache_index[key]
            self._save_disk_index()
    
    def _remove_from_session(self, key: str):
        """Remove key from session cache"""
        try:
            if 'enhanced_cache' in st.session_state and key in st.session_state.enhanced_cache:
                del st.session_state.enhanced_cache[key]
        except:
            pass
    
    def _get_memory_size(self) -> int:
        """Get total memory cache size"""
        return sum(entry.size_bytes for entry in self.memory_cache.values())
    
    def _evict_lru_memory(self):
        """Evict least recently used entries from memory"""
        if not self.memory_cache:
            return
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest 25% of entries
        evict_count = max(1, len(sorted_entries) // 4)
        
        for i in range(evict_count):
            key, entry = sorted_entries[i]
            
            # Demote to disk if not already there
            if key not in self.disk_cache_index and entry.cache_level != CacheLevel.SESSION:
                self._store_on_disk(key, entry)
            
            self._remove_from_memory(key)
            self.stats.evictions += 1
    
    def _evict_lru_if_needed(self):
        """Evict LRU entries if cache is too large"""
        if self._get_memory_size() > self.max_memory_size:
            self._evict_lru_memory()
    
    def _cleanup_expired(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        # Check memory cache
        for key, entry in self.memory_cache.items():
            if current_time > entry.expires_at:
                expired_keys.append(key)
        
        # Check disk cache
        for key, entry in self.disk_cache_index.items():
            if current_time > entry.expires_at:
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            self._remove_key(key)
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _update_avg_access_time(self, access_time: float):
        """Update average access time"""
        total_accesses = self.stats.hits + self.stats.misses
        if total_accesses == 1:
            self.stats.avg_access_time = access_time
        else:
            self.stats.avg_access_time = (
                (self.stats.avg_access_time * (total_accesses - 1) + access_time) / total_accesses
            )
    
    def _log_stats(self):
        """Log cache statistics"""
        stats = self.get_stats()
        self.logger.info(f"Cache stats: {stats['hit_rate']:.1f}% hit rate, "
                        f"{stats['memory_entries']} memory entries, "
                        f"{stats['disk_entries']} disk entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "hit_rate": self.stats.hit_rate,
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "evictions": self.stats.evictions,
            "invalidations": self.stats.invalidations,
            "memory_entries": len(self.memory_cache),
            "disk_entries": len(self.disk_cache_index),
            "memory_size_mb": self._get_memory_size() / (1024 * 1024),
            "max_memory_mb": self.max_memory_size / (1024 * 1024),
            "avg_access_time_ms": self.stats.avg_access_time * 1000,
            "dependencies_tracked": len(self.dependency_tracker.dependencies)
        }
    
    def clear(self, cache_level: Optional[CacheLevel] = None):
        """Clear cache entries"""
        if cache_level is None or cache_level == CacheLevel.MEMORY:
            self.memory_cache.clear()
        
        if cache_level is None or cache_level == CacheLevel.DISK:
            for cache_file in self.cache_dir.glob("*.pickle"):
                cache_file.unlink()
            self.disk_cache_index.clear()
            self._save_disk_index()
        
        if cache_level is None or cache_level == CacheLevel.SESSION:
            if 'enhanced_cache' in st.session_state:
                st.session_state.enhanced_cache.clear()

# Global cache instance
_cache_system = None

def get_cache_system() -> EnhancedCacheSystem:
    """Get or create the global cache system"""
    global _cache_system
    
    if _cache_system is None:
        _cache_system = EnhancedCacheSystem()
    
    return _cache_system

# Decorator for automatic caching
def smart_cache(ttl: int = 3600, 
                dependencies: List[str] = None,
                cache_level: CacheLevel = CacheLevel.MEMORY,
                key_func: Optional[Callable] = None):
    """
    Smart caching decorator with dependency tracking
    
    Args:
        ttl: Time to live in seconds
        dependencies: List of dependencies for invalidation
        cache_level: Which cache level to use
        key_func: Custom key generation function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_system = get_cache_system()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_system._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = cache_system.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_system.set(
                cache_key, 
                result, 
                ttl=ttl, 
                dependencies=dependencies,
                cache_level=cache_level
            )
            
            return result
        
        return wrapper
    return decorator

# Streamlit-specific caching wrapper
def streamlit_cache(ttl: int = 3600, dependencies: List[str] = None):
    """Streamlit-optimized cache decorator"""
    return smart_cache(
        ttl=ttl,
        dependencies=dependencies,
        cache_level=CacheLevel.SESSION
    )

# High-performance database cache
def database_cache(ttl: int = 300, dependencies: List[str] = None):
    """Database query cache decorator"""
    if dependencies is None:
        dependencies = ['database_updated']
    
    return smart_cache(
        ttl=ttl,
        dependencies=dependencies,
        cache_level=CacheLevel.MEMORY
    )

# Convenience functions
def invalidate_cache(dependencies: Union[str, List[str]]):
    """Invalidate cache entries by dependencies"""
    cache_system = get_cache_system()
    cache_system.invalidate(dependencies)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache system statistics"""
    cache_system = get_cache_system()
    return cache_system.get_stats()

def clear_cache(cache_level: Optional[CacheLevel] = None):
    """Clear cache entries"""
    cache_system = get_cache_system()
    cache_system.clear(cache_level)