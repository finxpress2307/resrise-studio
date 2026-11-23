"""Resrise Studio - Unified CLI for all automation commands."""
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core.config import load_settings, get_settings
from core.logging import configure_logging, get_logger
from agents.swarm import run_swarm, load_queue
from agents.browsing import run_browsing, BrowsingConfig
from agents.replying import run_replying
from agents.publishing import run_publishing
from dashboard.server import main as run_dashboard
from core.browser import open_login_browser, validate_account

app = typer.Typer(
    name="resrise",
    help="Resrise Studio - AI Creative Studio automation suite",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()
logger = get_logger("resrise.cli")


# Global options
@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    json_logs: bool = typer.Option(False, "--json-logs", help="Output logs as JSON"),
):
    """Configure global logging."""
    level = "DEBUG" if verbose else "INFO"
    configure_logging(level=level, json_output=json_logs)
    load_settings()  # Initialize settings


def validate_account_arg(account: str) -> str:
    """Validate account argument."""
    return validate_account(account)


# Login command
@app.command()
def login(
    account: str = typer.Argument(..., help="Instagram account handle", callback=validate_account_arg),
):
    """Open Chrome for manual Instagram login."""
    open_login_browser(account)


# Swarm command
@app.command()
def swarm(
    account: str = typer.Option("all", "--account", "-a", help="Account to run swarm for (or 'all')"),
    count: int = typer.Option(2, "--count", "-n", help="Number of drafts per account"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Generate drafts but don't save"),
):
    """Run the 4-agent swarm to generate post drafts."""
    settings = get_settings()
    config_accounts = list(load_settings().instagram_accounts)

    if account == "all":
        selected = config_accounts
    elif account in config_accounts:
        selected = [account]
    else:
        console.print(f"[red]Invalid account '{account}'. Choose from: {', '.join(config_accounts)} or 'all'[/red]")
        raise typer.Exit(1)

    run_swarm(selected, count, dry_run=dry_run)

    if not dry_run:
        console.print(f"\n[green]✅ Swarm complete. Review drafts with:[/green] [cyan]resrise dashboard[/cyan]")


# Dashboard command
@app.command()
def dashboard():
    """Start the approval dashboard web server."""
    run_dashboard()


# Browse command
@app.command()
def browse(
    account: str = typer.Argument(..., help="Instagram account handle", callback=validate_account_arg),
    max_batches: int = typer.Option(8, "--max-batches", help="Max batches to run (0 = unlimited)"),
    batch_size: int = typer.Option(4, "--batch-size", help="Posts per batch"),
    cooldown: int = typer.Option(240, "--cooldown", help="Cooldown seconds between batches"),
    draft_only: bool = typer.Option(False, "--draft-only", help="Save comments as drafts only"),
):
    """Run vision-aware feed browsing & commenting."""
    config = BrowsingConfig(
        max_batches=max_batches,
        batch_size=batch_size,
        cooldown_seconds=cooldown,
        draft_only=draft_only,
    )
    run_browsing(account, config)


# Reply command
@app.command()
def reply(
    account: str = typer.Argument(..., help="Instagram account handle", callback=validate_account_arg),
):
    """Run vision-aware comment replying."""
    run_replying(account)


# Publish command
@app.command()
def publish(
    account: str = typer.Argument(..., help="Instagram account handle", callback=validate_account_arg),
    dry_run: bool = typer.Option(False, "--dry-run", help="Upload and fill caption without clicking Share"),
):
    """Publish approved posts to Instagram."""
    run_publishing(account, dry_run=dry_run)


# Queue commands
@app.command("queue-list")
def queue_list(
    status: str = typer.Option("ALL", "--status", "-s", help="Filter by status"),
):
    """List drafts in the queue."""
    queue = load_queue()

    if status != "ALL":
        queue = [x for x in queue if x.get("status") == status]

    if not queue:
        console.print("[yellow]No drafts in queue[/yellow]")
        return

    table = Table(title="Draft Queue")
    table.add_column("ID", style="cyan")
    table.add_column("Account", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Viral Score", style="magenta")
    table.add_column("Pillar", style="blue")
    table.add_column("Format", style="white")
    table.add_column("Media", style="dim")

    for item in queue:
        media_count = len(item.get("media_paths", []))
        table.add_row(
            item.get("id", "")[:8],
            f"@{item.get('account', '')}",
            item.get("status", ""),
            str(item.get("viral_score", 0)),
            item.get("pillar", "")[:30],
            item.get("format", ""),
            f"{media_count} file(s)" if media_count else "none",
        )

    console.print(table)


@app.command("queue-clear")
def queue_clear(
    status: str = typer.Option("REJECTED", "--status", "-s", help="Clear drafts with this status"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Clear drafts from queue by status."""
    from core.config import save_queue

    queue = load_queue()
    to_remove = [x for x in queue if x.get("status") == status]

    if not to_remove:
        console.print(f"[yellow]No drafts with status '{status}'[/yellow]")
        return

    if not force:
        confirm = typer.confirm(f"Remove {len(to_remove)} draft(s) with status '{status}'?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            return

    queue = [x for x in queue if x.get("status") != status]
    save_queue(queue)
    console.print(f"[green]Removed {len(to_remove)} draft(s)[/green]")


# Config command
@app.command()
def config():
    """Show current configuration (with secrets masked)."""
    settings = get_settings()

    console.print("\n[bold]Resrise Studio Configuration[/bold]\n")

    table = Table(show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    # API keys (masked)
    or_key = settings.openrouter_api_key or settings.anthropic_auth_token
    table.add_row("OpenRouter API Key", f"{or_key[:8]}...{or_key[-4:]}" if or_key else "[red]NOT SET[/red]")
    table.add_row("OpenRouter Model", settings.openrouter_model)
    table.add_row("OmniRoute URL", settings.omniroute_url)
    table.add_row("Gemini API Key", f"{settings.gemini_api_key[:8]}..." if settings.gemini_api_key else "[dim]NOT SET[/dim]")
    table.add_row("Ollama URL", settings.ollama_url)

    console.print(table)

    console.print("\n[bold]Instagram Accounts:[/bold]")
    for acc in settings.instagram_accounts:
        console.print(f"  • @{acc}")

    console.print(f"\n[bold]Paths:[/bold]")
    console.print(f"  Project: {settings.project_dir}")
    console.print(f"  Draft Media: {settings.draft_media_dir}")
    console.print(f"  Queue: {settings.queue_path}")
    console.print(f"  Accounts Config: {settings.accounts_config_path}")


# Doctor command
@app.command()
def doctor():
    """Run health checks on the environment."""
    from core.vision import VisionClient
    from core.browser import BrowserManager, BrowserConfig

    console.print("\n[bold]Resrise Studio Health Check[/bold]\n")

    checks = []

    # Check .env file
    env_file = get_settings().project_dir / ".env"
    checks.append((".env file exists", env_file.exists()))

    # Check settings
    settings = get_settings()
    has_openrouter = bool(settings.openrouter_api_key or settings.anthropic_auth_token)
    checks.append(("OpenRouter API key configured", has_openrouter))

    # Check vision providers
    vision = VisionClient()
    available = vision.get_available_providers()
    checks.append(("Vision providers available", f"{', '.join(available) if available else 'NONE'}"))

    # Check Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome_found = any(Path(p).exists() for p in chrome_paths)
    checks.append(("Google Chrome installed", chrome_found))

    # Check Playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            checks.append(("Playwright installed", True))
    except ImportError:
        checks.append(("Playwright installed", False))

    # Check draft_media dirs
    for acc in settings.instagram_accounts:
        acc_dir = settings.draft_media_dir / acc
        checks.append((f"draft_media/{acc}/ exists", acc_dir.exists()))

    # Print results
    table = Table(show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column("Result", style="green")

    all_pass = True
    for name, result in checks:
        if isinstance(result, bool):
            status = "[green]✅ PASS[/green]" if result else "[red]❌ FAIL[/red]"
            if not result:
                all_pass = False
        else:
            status = f"[yellow]{result}[/yellow]"
        table.add_row(name, status)

    console.print(table)

    if all_pass:
        console.print("\n[green]All critical checks passed![/green]")
    else:
        console.print("\n[red]Some checks failed. Run with --verbose for details.[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()