#!/usr/bin/env python3
"""
Event System - Scalable Event-Driven Architecture
Provides event publishing, subscription, and processing for system components
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import queue
import uuid
from pathlib import Path
import weakref
import asyncio
import concurrent.futures

class EventType(Enum):
    """Standard event types"""
    # Data events
    COIN_ENRICHED = "coin_enriched"
    DATA_UPDATED = "data_updated"
    PRICE_CHANGED = "price_changed"
    
    # System events
    SYSTEM_STARTED = "system_started"
    SYSTEM_SHUTDOWN = "system_shutdown"
    HEALTH_CHECK_FAILED = "health_check_failed"
    
    # Cache events
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CACHE_INVALIDATED = "cache_invalidated"
    
    # Trading events
    SIGNAL_GENERATED = "signal_generated"
    TRADE_EXECUTED = "trade_executed"
    PORTFOLIO_UPDATED = "portfolio_updated"
    
    # Alert events
    PRICE_ALERT = "price_alert"
    VOLUME_SPIKE = "volume_spike"
    RUG_PULL_DETECTED = "rug_pull_detected"
    
    # Custom events
    CUSTOM = "custom"

@dataclass
class Event:
    """Event data structure"""
    event_type: Union[EventType, str]
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "unknown"
    priority: int = 5  # 1=highest, 10=lowest
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if isinstance(self.event_type, EventType):
            self.event_type = self.event_type.value

@dataclass
class EventSubscription:
    """Event subscription information"""
    subscriber_id: str
    event_types: List[str]
    callback: Callable[[Event], Any]
    filter_func: Optional[Callable[[Event], bool]] = None
    async_processing: bool = False
    max_queue_size: int = 1000
    created_at: datetime = field(default_factory=datetime.now)
    
    def matches(self, event: Event) -> bool:
        """Check if this subscription matches an event"""
        # Check event type
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Apply custom filter
        if self.filter_func and not self.filter_func(event):
            return False
        
        return True

@dataclass
class EventStats:
    """Event system statistics"""
    events_published: int = 0
    events_processed: int = 0
    events_failed: int = 0
    subscribers_active: int = 0
    average_processing_time: float = 0.0
    queue_size: int = 0
    uptime_seconds: int = 0

class EventProcessor:
    """Processes events for subscribers"""
    
    def __init__(self, subscription: EventSubscription):
        self.subscription = subscription
        self.event_queue = queue.Queue(maxsize=subscription.max_queue_size)
        self.processing_stats = {
            'processed': 0,
            'failed': 0,
            'total_time': 0.0
        }
        self.worker_thread = None
        self.active = False
        
        # Setup logging
        self.logger = logging.getLogger(f"event_processor_{subscription.subscriber_id}")
    
    def start(self):
        """Start event processing"""
        if self.active:
            return
        
        self.active = True
        
        if self.subscription.async_processing:
            self.worker_thread = threading.Thread(target=self._async_worker, daemon=True)
        else:
            self.worker_thread = threading.Thread(target=self._sync_worker, daemon=True)
        
        self.worker_thread.start()
        self.logger.info(f"Event processor started for {self.subscription.subscriber_id}")
    
    def stop(self):
        """Stop event processing"""
        self.active = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.logger.info(f"Event processor stopped for {self.subscription.subscriber_id}")
    
    def queue_event(self, event: Event) -> bool:
        """Queue an event for processing"""
        try:
            self.event_queue.put_nowait(event)
            return True
        except queue.Full:
            self.logger.warning(f"Event queue full for {self.subscription.subscriber_id}, dropping event")
            return False
    
    def _sync_worker(self):
        """Synchronous event processing worker"""
        while self.active:
            try:
                event = self.event_queue.get(timeout=1.0)
                self._process_event(event)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Sync worker error: {e}")
    
    def _async_worker(self):
        """Asynchronous event processing worker"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process_events():
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                while self.active:
                    try:
                        event = self.event_queue.get(timeout=1.0)
                        
                        # Process in thread pool
                        future = executor.submit(self._process_event, event)
                        await asyncio.wrap_future(future)
                        
                        self.event_queue.task_done()
                        
                    except queue.Empty:
                        continue
                    except Exception as e:
                        self.logger.error(f"Async worker error: {e}")
        
        try:
            loop.run_until_complete(process_events())
        finally:
            loop.close()
    
    def _process_event(self, event: Event):
        """Process a single event"""
        start_time = time.time()
        
        try:
            # Call subscriber callback
            result = self.subscription.callback(event)
            
            # Update stats
            processing_time = time.time() - start_time
            self.processing_stats['processed'] += 1
            self.processing_stats['total_time'] += processing_time
            
            self.logger.debug(f"Event {event.event_id} processed in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.processing_stats['failed'] += 1
            self.logger.error(f"Event processing failed for {event.event_id}: {e}")
            
            # Retry logic
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                self.logger.info(f"Retrying event {event.event_id} (attempt {event.retry_count})")
                
                # Requeue with delay
                time.sleep(min(2 ** event.retry_count, 60))  # Exponential backoff
                self.queue_event(event)
            else:
                self.logger.error(f"Max retries exceeded for event {event.event_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        avg_time = 0.0
        if self.processing_stats['processed'] > 0:
            avg_time = self.processing_stats['total_time'] / self.processing_stats['processed']
        
        return {
            'subscriber_id': self.subscription.subscriber_id,
            'queue_size': self.event_queue.qsize(),
            'processed': self.processing_stats['processed'],
            'failed': self.processing_stats['failed'],
            'average_processing_time': avg_time,
            'active': self.active
        }

class EventBus:
    """
    High-performance event bus with async processing and filtering
    """
    
    def __init__(self, 
                 max_history: int = 10000,
                 enable_persistence: bool = True,
                 persistence_path: str = "data/events"):
        
        self.max_history = max_history
        self.enable_persistence = enable_persistence
        self.persistence_path = Path(persistence_path)
        
        if self.enable_persistence:
            self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        # Core data structures  
        self.subscriptions = {}  # subscriber_id -> EventSubscription
        self.processors = {}     # subscriber_id -> EventProcessor
        self.event_history = []  # Recent events
        self.stats = EventStats()
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Event filtering and routing
        self.global_filters = []
        self.event_routes = {}  # event_type -> list of subscriber_ids
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Start time for uptime tracking
        self.start_time = time.time()
        
        # Background maintenance
        self._setup_maintenance()
        
        self.logger.info("Event bus initialized")
    
    def _setup_maintenance(self):
        """Setup background maintenance tasks"""
        def maintenance_worker():
            while True:
                try:
                    time.sleep(300)  # Run every 5 minutes
                    self._cleanup_history()
                    self._update_stats()
                    self._persist_events()
                except Exception as e:
                    self.logger.error(f"Maintenance worker error: {e}")
        
        maintenance_thread = threading.Thread(target=maintenance_worker, daemon=True)
        maintenance_thread.start()
    
    def subscribe(self, 
                  subscriber_id: str,
                  event_types: Union[str, List[str], EventType, List[EventType]],
                  callback: Callable[[Event], Any],
                  filter_func: Optional[Callable[[Event], bool]] = None,
                  async_processing: bool = False,
                  max_queue_size: int = 1000) -> bool:
        """
        Subscribe to events
        
        Args:
            subscriber_id: Unique identifier for subscriber
            event_types: Event type(s) to subscribe to
            callback: Function to call when event matches
            filter_func: Optional filter function
            async_processing: Whether to process events asynchronously
            max_queue_size: Maximum queue size for subscriber
        
        Returns:
            True if subscription successful
        """
        
        # Normalize event types
        if isinstance(event_types, (str, EventType)):
            event_types = [event_types]
        
        normalized_types = []
        for event_type in event_types:
            if isinstance(event_type, EventType):
                normalized_types.append(event_type.value)
            else:
                normalized_types.append(event_type)
        
        with self.lock:
            # Remove existing subscription if exists
            if subscriber_id in self.subscriptions:
                self.unsubscribe(subscriber_id)
            
            # Create subscription
            subscription = EventSubscription(
                subscriber_id=subscriber_id,
                event_types=normalized_types,
                callback=callback,
                filter_func=filter_func,
                async_processing=async_processing,
                max_queue_size=max_queue_size
            )
            
            # Create processor
            processor = EventProcessor(subscription)
            
            # Store subscription and processor
            self.subscriptions[subscriber_id] = subscription
            self.processors[subscriber_id] = processor
            
            # Update routing table
            for event_type in normalized_types:
                if event_type not in self.event_routes:
                    self.event_routes[event_type] = []
                self.event_routes[event_type].append(subscriber_id)
            
            # Start processor
            processor.start()
            
            self.stats.subscribers_active = len(self.subscriptions)
            
            self.logger.info(f"Subscriber {subscriber_id} registered for events: {normalized_types}")
            
            return True
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from events"""
        with self.lock:
            if subscriber_id not in self.subscriptions:
                return False
            
            # Stop processor
            if subscriber_id in self.processors:
                self.processors[subscriber_id].stop()
                del self.processors[subscriber_id]
            
            # Remove from routing table
            subscription = self.subscriptions[subscriber_id]
            for event_type in subscription.event_types:
                if event_type in self.event_routes:
                    if subscriber_id in self.event_routes[event_type]:
                        self.event_routes[event_type].remove(subscriber_id)
                    
                    # Clean up empty routes
                    if not self.event_routes[event_type]:
                        del self.event_routes[event_type]
            
            # Remove subscription
            del self.subscriptions[subscriber_id]
            
            self.stats.subscribers_active = len(self.subscriptions)
            
            self.logger.info(f"Subscriber {subscriber_id} unsubscribed")
            
            return True
    
    def publish(self, 
                event_type: Union[str, EventType],
                data: Dict[str, Any],
                source: str = "unknown",
                priority: int = 5) -> str:
        """
        Publish an event
        
        Args:
            event_type: Type of event
            data: Event data
            source: Event source identifier
            priority: Event priority (1=highest, 10=lowest)
        
        Returns:
            Event ID
        """
        
        # Create event
        event = Event(
            event_type=event_type,
            data=data,
            source=source,
            priority=priority
        )
        
        return self.publish_event(event)
    
    def publish_event(self, event: Event) -> str:
        """
        Publish an event object
        
        Args:
            event: Event to publish
        
        Returns:
            Event ID
        """
        
        with self.lock:
            # Apply global filters
            for filter_func in self.global_filters:
                if not filter_func(event):
                    self.logger.debug(f"Event {event.event_id} filtered out by global filter")
                    return event.event_id
            
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Update stats
            self.stats.events_published += 1
            
            # Route to subscribers
            routed_count = 0
            
            # Get subscribers for this event type
            subscribers = self.event_routes.get(event.event_type, [])
            
            # Also check for wildcard subscribers (subscribed to all events)
            if '*' in self.event_routes:
                subscribers.extend(self.event_routes['*'])
            
            for subscriber_id in subscribers:
                if subscriber_id not in self.subscriptions:
                    continue
                
                subscription = self.subscriptions[subscriber_id]
                
                # Check if subscription matches
                if subscription.matches(event):
                    processor = self.processors.get(subscriber_id)
                    if processor and processor.queue_event(event):
                        routed_count += 1
            
            self.logger.debug(f"Event {event.event_id} routed to {routed_count} subscribers")
            
            return event.event_id
    
    def add_global_filter(self, filter_func: Callable[[Event], bool]):
        """Add a global event filter"""
        self.global_filters.append(filter_func)
        self.logger.info("Global event filter added")
    
    def remove_global_filter(self, filter_func: Callable[[Event], bool]):
        """Remove a global event filter"""
        if filter_func in self.global_filters:
            self.global_filters.remove(filter_func)
            self.logger.info("Global event filter removed")
    
    def get_event_history(self, 
                         event_type: Optional[str] = None,
                         since: Optional[datetime] = None,
                         limit: Optional[int] = None) -> List[Event]:
        """Get event history with optional filtering"""
        
        with self.lock:
            events = self.event_history.copy()
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        if limit:
            events = events[:limit]
        
        return events
    
    def get_subscribers(self) -> List[Dict[str, Any]]:
        """Get list of active subscribers"""
        with self.lock:
            subscribers = []
            
            for subscriber_id, subscription in self.subscriptions.items():
                processor_stats = {}
                if subscriber_id in self.processors:
                    processor_stats = self.processors[subscriber_id].get_stats()
                
                subscribers.append({
                    'subscriber_id': subscriber_id,
                    'event_types': subscription.event_types,
                    'async_processing': subscription.async_processing,
                    'created_at': subscription.created_at.isoformat(),
                    **processor_stats
                })
            
            return subscribers
    
    def _cleanup_history(self):
        """Clean up old events from history"""
        if len(self.event_history) > self.max_history:
            with self.lock:
                excess = len(self.event_history) - self.max_history
                self.event_history = self.event_history[excess:]
                self.logger.debug(f"Cleaned up {excess} old events from history")
    
    def _update_stats(self):
        """Update system statistics"""
        with self.lock:
            total_processed = 0
            total_failed = 0
            total_time = 0.0
            total_queue_size = 0
            
            for processor in self.processors.values():
                stats = processor.get_stats()
                total_processed += stats['processed']
                total_failed += stats['failed']
                total_time += stats['average_processing_time'] * stats['processed']
                total_queue_size += stats['queue_size']
            
            self.stats.events_processed = total_processed
            self.stats.events_failed = total_failed
            self.stats.queue_size = total_queue_size
            self.stats.uptime_seconds = int(time.time() - self.start_time)
            
            if total_processed > 0:
                self.stats.average_processing_time = total_time / total_processed
    
    def _persist_events(self):
        """Persist recent events to disk"""
        if not self.enable_persistence:
            return
        
        try:
            # Save recent events (last 1000)
            recent_events = self.get_event_history(limit=1000)
            
            events_data = []
            for event in recent_events:
                events_data.append({
                    'event_type': event.event_type,
                    'data': event.data,
                    'timestamp': event.timestamp.isoformat(),
                    'event_id': event.event_id,
                    'source': event.source,
                    'priority': event.priority
                })
            
            events_file = self.persistence_path / "recent_events.json"
            with open(events_file, 'w') as f:
                json.dump(events_data, f, indent=2, default=str)
            
            self.logger.debug(f"Persisted {len(events_data)} events to disk")
            
        except Exception as e:
            self.logger.error(f"Failed to persist events: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive event bus statistics"""
        self._update_stats()
        
        with self.lock:
            return {
                'events_published': self.stats.events_published,
                'events_processed': self.stats.events_processed,
                'events_failed': self.stats.events_failed,
                'subscribers_active': self.stats.subscribers_active,
                'average_processing_time': self.stats.average_processing_time,
                'total_queue_size': self.stats.queue_size,
                'uptime_seconds': self.stats.uptime_seconds,
                'event_history_size': len(self.event_history),
                'success_rate': (
                    (self.stats.events_processed - self.stats.events_failed) / 
                    max(self.stats.events_processed, 1) * 100
                ),
                'events_per_second': (
                    self.stats.events_published / max(self.stats.uptime_seconds, 1)
                )
            }
    
    def shutdown(self):
        """Shutdown the event bus"""
        self.logger.info("Shutting down event bus...")
        
        # Publish shutdown event
        self.publish(EventType.SYSTEM_SHUTDOWN, {"timestamp": datetime.now().isoformat()})
        
        # Stop all processors
        with self.lock:
            for processor in self.processors.values():
                processor.stop()
        
        # Final persistence
        self._persist_events()
        
        self.logger.info("Event bus shutdown complete")

# Global event bus instance
_event_bus = None

def get_event_bus() -> EventBus:
    """Get or create the global event bus"""
    global _event_bus
    
    if _event_bus is None:
        _event_bus = EventBus()
    
    return _event_bus

# Convenience functions
def publish_event(event_type: Union[str, EventType], 
                 data: Dict[str, Any], 
                 source: str = "unknown") -> str:
    """Publish an event using the global event bus"""
    event_bus = get_event_bus()
    return event_bus.publish(event_type, data, source)

def subscribe_to_events(subscriber_id: str,
                       event_types: Union[str, List[str]],
                       callback: Callable[[Event], Any],
                       **kwargs) -> bool:
    """Subscribe to events using the global event bus"""
    event_bus = get_event_bus()
    return event_bus.subscribe(subscriber_id, event_types, callback, **kwargs)

def unsubscribe_from_events(subscriber_id: str) -> bool:
    """Unsubscribe from events using the global event bus"""
    event_bus = get_event_bus()
    return event_bus.unsubscribe(subscriber_id)

# Event decorators
def event_handler(event_types: Union[str, List[str]], 
                 subscriber_id: Optional[str] = None,
                 async_processing: bool = False):
    """Decorator to automatically register event handlers"""
    def decorator(func):
        handler_id = subscriber_id or f"{func.__module__}.{func.__name__}"
        
        # Register the handler
        subscribe_to_events(
            handler_id, 
            event_types, 
            func, 
            async_processing=async_processing
        )
        
        return func
    
    return decorator

def event_publisher(event_type: Union[str, EventType], source: str = "unknown"):
    """Decorator to automatically publish events when function is called"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Publish event with function result
            publish_event(
                event_type,
                {
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                    'result': result
                },
                source
            )
            
            return result
        
        return wrapper
    
    return decorator