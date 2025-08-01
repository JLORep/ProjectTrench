#!/usr/bin/env python3
"""
TrenchCoat Coin Enrichment Script
Enriches coins.db with data from multiple free APIs
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.master_enricher import MasterEnricher, EnrichmentStats
from config.config import settings

console = Console()

class RichProgressTracker:
    """Rich-based progress tracker for enrichment"""
    
    def __init__(self):
        self.stats = None
        self.layout = Layout()
        self.setup_layout()
        
    def setup_layout(self):
        """Setup the rich layout"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        self.layout["body"].split_row(
            Layout(name="progress"),
            Layout(name="stats")
        )
        
    def update_display(self, stats: EnrichmentStats):
        """Update the display with current stats"""
        self.stats = stats
        
        # Header
        self.layout["header"].update(
            Panel(
                "🔮 TrenchCoat Coin Enrichment Engine",
                style="bold blue",
                subtitle=f"Powered by {len(['CoinGecko', 'DexScreener', 'Jupiter', 'Solscan', 'CryptoCompare'])} Free APIs"
            )
        )
        
        # Progress section
        progress_text = f"""
[bold green]Progress Overview[/bold green]

📊 Total Coins: {stats.total_coins}
✅ Processed: {stats.processed}
🎯 Successful: {stats.successful}
❌ Failed: {stats.failed}

📈 Success Rate: {stats.success_rate:.1%}
⏱️  Time Elapsed: {stats.elapsed_time}
🚀 Rate: {stats.coins_per_minute:.1f} coins/minute
        """
        
        if stats.total_coins > 0:
            progress_percent = (stats.processed / stats.total_coins) * 100
            progress_bar = "█" * int(progress_percent / 2) + "░" * (50 - int(progress_percent / 2))
            progress_text += f"\n🔋 [{progress_bar}] {progress_percent:.1f}%"
        
        self.layout["progress"].update(Panel(progress_text.strip(), title="Progress"))
        
        # Stats section
        stats_table = Table(title="Live Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")
        
        stats_table.add_row("🎯 Success Rate", f"{stats.success_rate:.2%}")
        stats_table.add_row("⚡ Speed", f"{stats.coins_per_minute:.1f}/min")
        stats_table.add_row("⏰ ETA", self._calculate_eta(stats))
        stats_table.add_row("🔥 Status", "🟢 Active" if stats.processed < stats.total_coins else "✅ Complete")
        
        self.layout["stats"].update(stats_table)
        
        # Footer
        footer_text = f"Last updated: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to stop"
        self.layout["footer"].update(Panel(footer_text, style="dim"))
    
    def _calculate_eta(self, stats: EnrichmentStats) -> str:
        """Calculate estimated time to completion"""
        if stats.coins_per_minute == 0 or stats.processed >= stats.total_coins:
            return "N/A"
        
        remaining = stats.total_coins - stats.processed
        eta_minutes = remaining / stats.coins_per_minute
        
        if eta_minutes < 1:
            return f"{eta_minutes * 60:.0f}s"
        elif eta_minutes < 60:
            return f"{eta_minutes:.1f}m"
        else:
            hours = eta_minutes / 60
            return f"{hours:.1f}h"

async def enrich_all_coins(args):
    """Enrich all coins in database"""
    console.print("🚀 Starting comprehensive coin enrichment...", style="bold green")
    
    enricher = MasterEnricher(args.db_path)
    progress_tracker = RichProgressTracker()
    
    def update_callback(stats: EnrichmentStats):
        progress_tracker.update_display(stats)
    
    try:
        with Live(progress_tracker.layout, refresh_per_second=2, console=console):
            stats = await enricher.enrich_all_coins(
                max_coins=args.max_coins,
                priority_filter=args.priority,
                progress_callback=update_callback
            )
        
        # Final summary
        display_final_summary(stats)
        
    except KeyboardInterrupt:
        console.print("\n⚠️ Enrichment interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error during enrichment: {e}", style="red")

async def enrich_specific_coins(args):
    """Enrich specific coins by address"""
    console.print(f"🎯 Enriching {len(args.addresses)} specific coins...", style="bold blue")
    
    enricher = MasterEnricher(args.db_path)
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("Enriching coins...", total=len(args.addresses))
        
        def update_callback(stats: EnrichmentStats):
            progress.update(task, completed=stats.processed)
        
        stats = await enricher.enrich_specific_coins(args.addresses)
        progress.update(task, completed=stats.total_coins)
    
    display_final_summary(stats)

async def generate_report(args):
    """Generate enrichment report"""
    console.print("📊 Generating enrichment report...", style="bold blue")
    
    enricher = MasterEnricher(args.db_path)
    report = await enricher.get_enrichment_report()
    
    # Display report
    console.print("\n" + "="*60)
    console.print("📈 ENRICHMENT REPORT", style="bold green", justify="center")
    console.print("="*60)
    
    # Coverage section
    coverage = report['enrichment_coverage']
    console.print(f"\n🎯 [bold]Coverage Overview[/bold]")
    console.print(f"   Total coins in database: {coverage['total_coins']:,}")
    console.print(f"   Enriched in last 24h: {coverage['enriched_24h']:,}")
    console.print(f"   Coverage percentage: {coverage['coverage_percentage']:.1f}%")
    
    # Data quality section
    quality = report['data_quality']
    console.print(f"\n⭐ [bold]Data Quality[/bold]")
    console.print(f"   Average enrichment score: {quality['average_score']:.2f}")
    console.print(f"   Score range: {quality['min_score']:.2f} - {quality['max_score']:.2f}")
    
    # Data sources section
    console.print(f"\n🔗 [bold]Data Sources[/bold]")
    for source in report['data_sources'][:5]:  # Top 5
        sources_list = ', '.join(source['sources'])
        console.print(f"   {sources_list}: {source['count']} coins")
    
    # Pending enrichment
    pending = report['pending_enrichment'][:10]  # Top 10
    if pending:
        console.print(f"\n⏳ [bold]Coins Needing Enrichment[/bold]")
        for coin in pending:
            console.print(f"   {coin['symbol']}: {coin['last_attempt'] or 'Never'}")
    
    console.print(f"\n📅 Report generated: {report['report_generated']}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        console.print(f"\n💾 Report saved to: {args.output}")

def display_final_summary(stats: EnrichmentStats):
    """Display final enrichment summary"""
    console.print("\n" + "="*50)
    console.print("🎉 ENRICHMENT COMPLETE", style="bold green", justify="center")
    console.print("="*50)
    
    # Create summary table
    table = Table(title="Final Statistics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="yellow")
    table.add_column("Details", style="dim")
    
    table.add_row("Total Coins", f"{stats.total_coins:,}", "Coins in queue")
    table.add_row("Processed", f"{stats.processed:,}", f"{stats.processed/stats.total_coins:.1%} of total")
    table.add_row("Successful", f"{stats.successful:,}", f"{stats.success_rate:.1%} success rate")
    table.add_row("Failed", f"{stats.failed:,}", "Needs manual review")
    table.add_row("Duration", str(stats.elapsed_time).split('.')[0], f"{stats.coins_per_minute:.1f} coins/min")
    
    console.print(table)
    
    # Recommendations
    if stats.failed > 0:
        console.print(f"\n💡 [yellow]Recommendations:[/yellow]")
        console.print(f"   • Review failed coins for missing contract addresses")
        console.print(f"   • Consider running enrichment again for failed coins")
        console.print(f"   • Check API rate limits if many failures occurred")
    
    if stats.success_rate > 0.8:
        console.print(f"\n🎊 [green]Excellent![/green] High success rate achieved.")
    elif stats.success_rate > 0.6:
        console.print(f"\n👍 [blue]Good![/blue] Decent enrichment coverage.")
    else:
        console.print(f"\n⚠️ [yellow]Warning![/yellow] Low success rate - check data sources.")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="TrenchCoat Coin Enrichment Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enrich all coins
  python scripts/enrich_coins.py --all
  
  # Enrich high priority coins only
  python scripts/enrich_coins.py --all --priority 1
  
  # Enrich specific coins
  python scripts/enrich_coins.py --addresses EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R
  
  # Generate report
  python scripts/enrich_coins.py --report --output report.json
  
  # Limit processing
  python scripts/enrich_coins.py --all --max-coins 100
        """
    )
    
    # Command group
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument("--all", action="store_true", 
                              help="Enrich all coins in database")
    command_group.add_argument("--addresses", nargs="+", 
                              help="Specific contract addresses to enrich")
    command_group.add_argument("--report", action="store_true",
                              help="Generate enrichment report")
    
    # Options
    parser.add_argument("--max-coins", type=int, 
                       help="Maximum number of coins to process")
    parser.add_argument("--priority", type=int, choices=[1, 2, 3],
                       help="Priority filter: 1=high, 2=medium, 3=low")
    parser.add_argument("--db-path", 
                       help="Path to database file (default: data/coins.db)")
    parser.add_argument("--output", 
                       help="Output file for report (JSON format)")
    
    args = parser.parse_args()
    
    # Welcome message
    console.print(Panel.fit(
        "[bold blue]TrenchCoat Coin Enrichment Engine[/bold blue]\n"
        "Powered by multiple free crypto APIs\n"
        f"Database: {args.db_path or 'data/coins.db'}",
        border_style="blue"
    ))
    
    # Run appropriate command
    try:
        if args.all:
            asyncio.run(enrich_all_coins(args))
        elif args.addresses:
            asyncio.run(enrich_specific_coins(args))
        elif args.report:
            asyncio.run(generate_report(args))
    except KeyboardInterrupt:
        console.print("\nGoodbye!", style="bold blue")
        sys.exit(0)
    except Exception as e:
        console.print(f"\nFatal error: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()