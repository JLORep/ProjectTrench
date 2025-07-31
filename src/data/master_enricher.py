import asyncio
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from dataclasses import dataclass
import json
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import sys
import traceback

from src.data.free_api_providers import FreeAPIProviders
from src.data.database import CoinDatabase
from config.config import settings

@dataclass
class EnrichmentTask:
    contract_address: str
    symbol: str
    priority: int = 1  # 1=high, 2=medium, 3=low
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    status: str = "pending"  # pending, processing, completed, failed

@dataclass
class EnrichmentStats:
    total_coins: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: datetime = None
    
    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return self.successful / self.processed
    
    @property
    def elapsed_time(self) -> timedelta:
        if self.start_time:
            return datetime.now() - self.start_time
        return timedelta(0)
    
    @property
    def coins_per_minute(self) -> float:
        elapsed = self.elapsed_time.total_seconds() / 60
        if elapsed > 0:
            return self.processed / elapsed
        return 0.0

class MasterEnricher:
    """
    Master orchestrator for enriching coins.db with data from all free APIs
    Handles prioritization, rate limiting, error recovery, and progress tracking
    """
    
    def __init__(self, db_path: str = None):
        self.db = CoinDatabase(db_path=Path(db_path) if db_path else None)
        self.stats = EnrichmentStats()
        self.task_queue: List[EnrichmentTask] = []
        self.max_concurrent = 5  # Concurrent API calls
        self.max_retries = 3
        self.batch_size = 10
        self.progress_callback = None
        
    async def load_coins_from_db(self) -> List[EnrichmentTask]:
        """Load coins from database and create enrichment tasks"""
        logger.info("Loading coins from database...")
        
        with sqlite3.connect(self.db.db_path) as conn:
            # Get coins that need enrichment (no recent enrichment or failed)
            query = """
            SELECT 
                c.symbol,
                c.name,
                COALESCE(pd.contract_address, c.symbol) as contract_address,
                c.updated_at,
                COUNT(pd.id) as price_data_points
            FROM coins c
            LEFT JOIN price_data pd ON c.id = pd.coin_id
            WHERE c.symbol IS NOT NULL
            GROUP BY c.id, c.symbol, c.name
            ORDER BY 
                CASE 
                    WHEN c.updated_at IS NULL THEN 1
                    WHEN datetime(c.updated_at) < datetime('now', '-1 hour') THEN 2
                    ELSE 3
                END,
                c.market_cap DESC NULLS LAST
            """
            
            df = pd.read_sql_query(query, conn)
        
        tasks = []
        for _, row in df.iterrows():
            # Determine priority based on data freshness and market cap
            priority = 1  # High priority by default
            
            if row['updated_at'] is not None:
                last_update = pd.to_datetime(row['updated_at'])
                hours_old = (datetime.now() - last_update).total_seconds() / 3600
                
                if hours_old < 1:
                    priority = 3  # Low priority - recently updated
                elif hours_old < 6:
                    priority = 2  # Medium priority
            
            task = EnrichmentTask(
                contract_address=row['contract_address'],
                symbol=row['symbol'],
                priority=priority
            )
            
            tasks.append(task)
        
        logger.info(f"Created {len(tasks)} enrichment tasks")
        return tasks
    
    async def enrich_all_coins(self, 
                              max_coins: Optional[int] = None,
                              priority_filter: Optional[int] = None,
                              progress_callback=None) -> EnrichmentStats:
        """
        Main method to enrich all coins in the database
        """
        logger.info("🚀 Starting master enrichment process...")
        
        self.stats = EnrichmentStats(start_time=datetime.now())
        self.progress_callback = progress_callback
        
        # Load tasks
        self.task_queue = await self.load_coins_from_db()
        
        # Apply filters
        if priority_filter:
            self.task_queue = [t for t in self.task_queue if t.priority <= priority_filter]
        
        if max_coins:
            self.task_queue = self.task_queue[:max_coins]
        
        self.stats.total_coins = len(self.task_queue)
        
        if not self.task_queue:
            logger.warning("No coins to enrich")
            return self.stats
        
        logger.info(f"Enriching {self.stats.total_coins} coins with max {self.max_concurrent} concurrent requests")
        
        # Process in batches to manage memory and rate limits
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with FreeAPIProviders() as api_provider:
            # Process tasks in batches
            for i in range(0, len(self.task_queue), self.batch_size):
                batch = self.task_queue[i:i + self.batch_size]
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(self.task_queue)-1)//self.batch_size + 1}")
                
                # Create tasks for concurrent processing
                batch_tasks = [
                    self._process_single_coin(task, api_provider, semaphore)
                    for task in batch
                ]
                
                # Execute batch concurrently
                await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Progress update
                if self.progress_callback:
                    self.progress_callback(self.stats)
                
                # Brief pause between batches to be respectful to APIs
                await asyncio.sleep(1)
        
        # Final statistics
        self._log_final_stats()
        
        return self.stats
    
    async def _process_single_coin(self, 
                                  task: EnrichmentTask, 
                                  api_provider: FreeAPIProviders,
                                  semaphore: asyncio.Semaphore) -> bool:
        """Process a single coin enrichment task"""
        async with semaphore:
            return await self._enrich_coin_with_retry(task, api_provider)
    
    async def _enrich_coin_with_retry(self, 
                                    task: EnrichmentTask, 
                                    api_provider: FreeAPIProviders) -> bool:
        """Enrich a single coin with retry logic"""
        max_attempts = self.max_retries + 1
        
        for attempt in range(max_attempts):
            try:
                task.status = "processing"
                task.last_attempt = datetime.now()
                
                # Get comprehensive data from all APIs
                enriched_data = await api_provider.get_comprehensive_data(
                    task.contract_address, 
                    task.symbol
                )
                
                if enriched_data and enriched_data.get('enrichment_score', 0) > 0:
                    # Save to database
                    success = await self._save_enriched_data(task, enriched_data)
                    
                    if success:
                        task.status = "completed"
                        self.stats.successful += 1
                        self.stats.processed += 1
                        
                        logger.info(
                            f"✅ {task.symbol} enriched successfully "
                            f"(Score: {enriched_data.get('enrichment_score', 0):.2f}, "
                            f"Sources: {len(enriched_data.get('data_sources', []))})"
                        )
                        
                        return True
                    else:
                        logger.warning(f"Failed to save data for {task.symbol}")
                else:
                    logger.warning(f"No data retrieved for {task.symbol}")
                
            except Exception as e:
                logger.error(f"Error enriching {task.symbol} (attempt {attempt + 1}): {str(e)}")
                
                # Log full traceback for debugging
                if attempt == 0:  # Only log full traceback on first attempt
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                
                # Wait before retry (exponential backoff)
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
        
        # All attempts failed
        task.status = "failed"
        task.retry_count = max_attempts
        self.stats.failed += 1
        self.stats.processed += 1
        
        logger.error(f"❌ Failed to enrich {task.symbol} after {max_attempts} attempts")
        return False
    
    async def _save_enriched_data(self, task: EnrichmentTask, data: Dict[str, Any]) -> bool:
        """Save enriched data to database"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Get or create coin
                cursor.execute("""
                    INSERT OR IGNORE INTO coins (symbol, name) 
                    VALUES (?, ?)
                """, (task.symbol, data.get('name', task.symbol)))
                
                # Get coin ID
                cursor.execute("SELECT id FROM coins WHERE symbol = ?", (task.symbol,))
                result = cursor.fetchone()
                if not result:
                    logger.error(f"Could not find or create coin record for {task.symbol}")
                    return False
                
                coin_id = result[0]
                
                # Update coin with enriched data
                cursor.execute("""
                    UPDATE coins SET
                        name = COALESCE(?, name),
                        market_cap = ?,
                        volume_24h = ?,
                        circulating_supply = ?,
                        max_supply = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    data.get('name'),
                    data.get('market_cap'),
                    data.get('volume_24h'),
                    data.get('total_supply'),
                    data.get('total_supply'),  # Use total_supply as max_supply if available
                    datetime.now(),
                    coin_id
                ))
                
                # Add current price data point
                if data.get('price'):
                    cursor.execute("""
                        INSERT OR REPLACE INTO price_data (
                            coin_id, timestamp, timeframe, open, high, low, close, volume
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        coin_id,
                        datetime.now(),
                        '1h',
                        data.get('price'),  # Use current price for OHLC
                        data.get('price'),
                        data.get('price'),
                        data.get('price'),
                        data.get('volume_24h', 0)
                    ))
                
                # Store metadata as JSON
                metadata = {
                    'enrichment_data': data,
                    'last_enriched': datetime.now().isoformat(),
                    'data_sources': data.get('data_sources', []),
                    'enrichment_score': data.get('enrichment_score', 0),
                    'data_quality': data.get('data_quality', {})
                }
                
                # Store in a metadata table (create if doesn't exist)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS coin_metadata (
                        coin_id INTEGER PRIMARY KEY,
                        metadata JSON,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (coin_id) REFERENCES coins(id)
                    )
                """)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO coin_metadata (coin_id, metadata, updated_at)
                    VALUES (?, ?, ?)
                """, (coin_id, json.dumps(metadata), datetime.now()))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving data for {task.symbol}: {e}")
            return False
    
    def _log_final_stats(self):
        """Log final enrichment statistics"""
        logger.info("🎉 Enrichment process completed!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   Total coins: {self.stats.total_coins}")
        logger.info(f"   Processed: {self.stats.processed}")
        logger.info(f"   Successful: {self.stats.successful}")
        logger.info(f"   Failed: {self.stats.failed}")
        logger.info(f"   Success rate: {self.stats.success_rate:.2%}")
        logger.info(f"   Total time: {self.stats.elapsed_time}")
        logger.info(f"   Rate: {self.stats.coins_per_minute:.1f} coins/minute")
    
    async def enrich_specific_coins(self, coin_addresses: List[str]) -> EnrichmentStats:
        """Enrich specific coins by their contract addresses"""
        logger.info(f"Enriching {len(coin_addresses)} specific coins...")
        
        self.stats = EnrichmentStats(start_time=datetime.now())
        
        # Create tasks for specific coins
        tasks = []
        for address in coin_addresses:
            # Try to get symbol from database
            symbol = await self._get_symbol_for_address(address)
            
            task = EnrichmentTask(
                contract_address=address,
                symbol=symbol or f"${address[:8]}",
                priority=1  # High priority for specific requests
            )
            tasks.append(task)
        
        self.task_queue = tasks
        self.stats.total_coins = len(tasks)
        
        # Process the tasks
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with FreeAPIProviders() as api_provider:
            batch_tasks = [
                self._process_single_coin(task, api_provider, semaphore)
                for task in tasks
            ]
            
            await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        self._log_final_stats()
        return self.stats
    
    async def _get_symbol_for_address(self, address: str) -> Optional[str]:
        """Get symbol for a contract address from database"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT symbol FROM coins 
                    WHERE symbol = ? OR name LIKE ?
                    LIMIT 1
                """, (address, f"%{address}%"))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception:
            return None
    
    async def get_enrichment_report(self) -> Dict[str, Any]:
        """Generate detailed enrichment report"""
        with sqlite3.connect(self.db.db_path) as conn:
            # Get enrichment statistics
            enriched_count = conn.execute("""
                SELECT COUNT(*) FROM coin_metadata 
                WHERE datetime(updated_at) > datetime('now', '-24 hours')
            """).fetchone()[0]
            
            total_count = conn.execute("SELECT COUNT(*) FROM coins").fetchone()[0]
            
            # Get data source coverage
            source_stats = conn.execute("""
                SELECT 
                    json_extract(metadata, '$.enrichment_data.data_sources') as sources,
                    COUNT(*) as count
                FROM coin_metadata 
                WHERE sources IS NOT NULL
                GROUP BY sources
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            # Get enrichment scores
            score_stats = conn.execute("""
                SELECT 
                    AVG(CAST(json_extract(metadata, '$.enrichment_data.enrichment_score') AS REAL)) as avg_score,
                    MIN(CAST(json_extract(metadata, '$.enrichment_data.enrichment_score') AS REAL)) as min_score,
                    MAX(CAST(json_extract(metadata, '$.enrichment_data.enrichment_score') AS REAL)) as max_score
                FROM coin_metadata 
                WHERE json_extract(metadata, '$.enrichment_data.enrichment_score') IS NOT NULL
            """).fetchone()
            
            # Get recent failures
            recent_failures = conn.execute("""
                SELECT 
                    c.symbol,
                    json_extract(cm.metadata, '$.last_enriched') as last_attempt
                FROM coins c
                LEFT JOIN coin_metadata cm ON c.id = cm.coin_id
                WHERE cm.coin_id IS NULL OR 
                      datetime(json_extract(cm.metadata, '$.last_enriched')) < datetime('now', '-6 hours')
                ORDER BY c.market_cap DESC NULLS LAST
                LIMIT 20
            """).fetchall()
        
        return {
            'enrichment_coverage': {
                'total_coins': total_count,
                'enriched_24h': enriched_count,
                'coverage_percentage': (enriched_count / total_count * 100) if total_count > 0 else 0
            },
            'data_quality': {
                'average_score': score_stats[0] if score_stats[0] else 0,
                'min_score': score_stats[1] if score_stats[1] else 0,
                'max_score': score_stats[2] if score_stats[2] else 0
            },
            'data_sources': [
                {'sources': json.loads(s[0]) if s[0] else [], 'count': s[1]} 
                for s in source_stats
            ],
            'pending_enrichment': [
                {'symbol': f[0], 'last_attempt': f[1]} 
                for f in recent_failures
            ],
            'report_generated': datetime.now().isoformat()
        }

# CLI interface for standalone usage
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Coin Enricher")
    parser.add_argument("--max-coins", type=int, help="Maximum number of coins to enrich")
    parser.add_argument("--priority", type=int, choices=[1, 2, 3], help="Priority filter (1=high, 2=medium, 3=low)")
    parser.add_argument("--addresses", nargs="+", help="Specific contract addresses to enrich")
    parser.add_argument("--report", action="store_true", help="Generate enrichment report")
    parser.add_argument("--db-path", help="Path to database file")
    
    args = parser.parse_args()
    
    enricher = MasterEnricher(args.db_path)
    
    if args.report:
        report = await enricher.get_enrichment_report()
        print(json.dumps(report, indent=2))
        return
    
    # Progress callback for CLI
    def progress_callback(stats: EnrichmentStats):
        print(f"Progress: {stats.processed}/{stats.total_coins} "
              f"({stats.success_rate:.1%} success rate, "
              f"{stats.coins_per_minute:.1f} coins/min)")
    
    if args.addresses:
        await enricher.enrich_specific_coins(args.addresses)
    else:
        await enricher.enrich_all_coins(
            max_coins=args.max_coins,
            priority_filter=args.priority,
            progress_callback=progress_callback
        )

if __name__ == "__main__":
    asyncio.run(main())