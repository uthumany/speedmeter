"""SpeedMeter Textual TUI Application — interactive internet speed meter."""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    RichLog,
    Static,
)

from speedmeter.config import get_default_config
from speedmeter.history import HistoryManager
from speedmeter.tester import SpeedTester, SpeedTestResult
from speedmeter.widgets import ServerInfoWidget, SpeedChart, SpeedGauge, SystemStatusWidget

logger = logging.getLogger(__name__)

# Color theme
THEME_DARK = {
    "primary": "#00ff87",
    "secondary": "#00d4ff",
    "accent": "#ff6b6b",
    "background": "#1a1b26",
    "surface": "#24253a",
    "text": "#c0caf5",
    "text_dim": "#565f89",
    "success": "#9ece6a",
    "warning": "#e0af68",
    "error": "#f7768e",
}


class TestResultCard(Static):
    """A card widget displaying a single speed test result."""

    def __init__(self, result: SpeedTestResult, precision: int = 2):
        super().__init__()
        self.result = result
        self.precision = precision

    def render(self):
        """Render the result card."""
        r = self.result
        if r.error:
            return Panel(
                Text(f"Error: {r.error}", style="red bold"),
                title="Test Failed",
                border_style="red",
            )

        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="bold")
        grid.add_column()

        dl_color = "green" if r.download_mbps >= 50 else "yellow" if r.download_mbps >= 10 else "red"
        ul_color = "green" if r.upload_mbps >= 20 else "yellow" if r.upload_mbps >= 5 else "red"

        grid.add_row("Download:", Text(f"{r.download_mbps:.{self.precision}f} Mbps", style=f"bold {dl_color}"))
        grid.add_row("Upload:", Text(f"{r.upload_mbps:.{self.precision}f} Mbps", style=f"bold {ul_color}"))
        grid.add_row("Ping:", Text(f"{r.ping_ms:.1f} ms", style="cyan"))
        if r.jitter_ms > 0:
            grid.add_row("Jitter:", Text(f"{r.jitter_ms:.1f} ms", style="dim"))
        grid.add_row("Server:", f"{r.server_name}")
        grid.add_row("Duration:", f"{r.duration_seconds:.1f}s")

        ts = time.strftime("%H:%M:%S", time.localtime(r.timestamp))
        return Panel(
            grid,
            title=f"Test at {ts}",
            border_style="blue",
        )


class HistoryScreen(Screen):
    """Screen showing test history."""

    def __init__(self, history: HistoryManager):
        super().__init__()
        self.history = history

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(id="history-container")
        yield Footer()

    def on_mount(self) -> None:
        """Populate history list."""
        container = self.query_one("#history-container")
        results = self.history.get_all()
        if not results:
            container.mount(Static("[dim]No tests recorded yet.[/dim]"))
        for result in results:
            container.mount(TestResultCard(result))


class ConfigScreen(Screen):
    """Screen for viewing/editing configuration."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("[bold]Configuration[/bold]", id="config-title"),
            Static("Edit speedmeter configuration here."),
            id="config-container",
        )
        yield Footer()


class SpeedMeterApp(App):
    """Main SpeedMeter TUI application."""

    CSS = """
    Screen {
        background: #1a1b26;
    }

    /* Main layout */
    #main-container {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
        height: 100%;
    }

    #top-left {
        height: 100%;
    }

    #top-right {
        height: 100%;
    }

    #bottom-panel {
        column-span: 2;
        height: auto;
        max-height: 12;
    }

    /* Status bar */
    #status-bar {
        height: 1;
        background: #24253a;
        color: #565f89;
        text-align: center;
        padding: 0 1;
    }

    /* Buttons */
    Button {
        margin: 0 1;
    }

    #test-button {
        background: #00ff87;
        color: #1a1b26;
        text-style: bold;
    }

    #stop-button {
        background: #f7768e;
        color: #1a1b26;
        text-style: bold;
    }

    /* Control bar */
    #controls {
        height: 3;
        align: center middle;
        padding: 0 1;
    }

    /* Speed gauges row */
    #gauges {
        height: auto;
    }

    Gauge {
        width: 1fr;
    }

    /* Info bar at bottom */
    #info-bar {
        height: auto;
        background: #24253a;
        padding: 0 1;
    }

    /* History container scrolling */
    ListView {
        border: solid #565f89;
        height: 100%;
    }

    /* Rich log for history */
    RichLog {
        border: solid #565f89;
        height: 100%;
    }

    /* Error state */
    .error-text {
        color: #f7768e;
    }
    .success-text {
        color: #9ece6a;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "run_test", "Run Test", show=True),
        Binding("s", "show_history", "History", show=True),
        Binding("c", "show_config", "Config", show=True),
        Binding("d", "toggle_detail", "Detail", show=True),
        Binding("space", "run_test", "Run", show=True),
    ]

    # Reactive properties
    is_testing = reactive(False)
    status_message = reactive("Ready. Press [b]Space[/] or [b]R[/] to run a speed test.")

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        server_id: Optional[int] = None,
        output: Optional[str] = None,
    ):
        super().__init__()
        self.config = config or get_default_config()
        self.server_id = server_id
        self.output = output
        self.history = HistoryManager(
            max_size=self.config.get("app", {}).get("history_size", 50),
        )
        self.tester = SpeedTester(
            server_id=self.server_id,
            timeout=self.config.get("app", {}).get("timeout", 30),
        )
        self._test_task: Optional[asyncio.Task] = None
        self._progress_value = 0.0
        self._progress_stage = ""
        self._show_detail = False

    def compose(self) -> ComposeResult:
        """Create the application layout."""
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical(id="top-left"):
                # Speed gauges
                with Horizontal(id="gauges"):
                    yield SpeedGauge(
                        label="Download",
                        unit="Mbps",
                        max_value=1000.0,
                        id="dl-gauge",
                    )
                    yield SpeedGauge(
                        label="Upload",
                        unit="Mbps",
                        max_value=500.0,
                        id="ul-gauge",
                    )
                    yield SpeedGauge(
                        label="Ping",
                        unit="ms",
                        max_value=200.0,
                        danger_threshold=100.0,
                        warning_threshold=50.0,
                        id="ping-gauge",
                    )
                # Speed chart
                yield SpeedChart(max_points=30, label="Speed History", id="speed-chart")
            with Vertical(id="top-right"):
                yield ServerInfoWidget(id="server-info")
                yield SystemStatusWidget(id="sys-status")
            # Bottom panel
            with Vertical(id="bottom-panel"):
                yield RichLog(id="status-log", highlight=True, markup=True, max_lines=5)
                with Horizontal(id="controls"):
                    yield Button("Run Test [bold](Space)[/]", id="test-button", variant="success")
                    yield Button("Stop", id="stop-button", variant="error", disabled=True)
                    yield Button("History [bold](S)[/]", id="history-button")
                    yield Button("Quick Mode", id="quick-button")
        yield Footer(id="app-footer")

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#status-log", RichLog).write("[bold cyan]SpeedMeter[/bold cyan] v1.0.0 — Internet Speed Meter")
        self.query_one("#status-log", RichLog).write(
            "[dim]Press [b]Space[/b] or [b]R[/b] to run a speed test. [b]Q[/b] to quit.[/dim]"
        )
        self.set_interval(5, self._update_system_stats)
        self.set_interval(1, self._tick_animations)

    def _tick_animations(self) -> None:
        """Tick gauge animations."""
        for gauge_id in ["dl-gauge", "ul-gauge", "ping-gauge"]:
            try:
                gauge = self.query_one(f"#{gauge_id}", SpeedGauge)
                if gauge.animation_progress < 1.0:
                    gauge.animation_progress = min(1.0, gauge.animation_progress + 0.15)
            except Exception:
                pass

    def _update_system_stats(self) -> None:
        """Periodically refresh system stats."""
        try:
            sys_widget = self.query_one("#sys-status", SystemStatusWidget)
            sys_widget.refresh()
        except Exception:
            pass

    def _log(self, message: str) -> None:
        """Write a message to the status log."""
        try:
            log = self.query_one("#status-log", RichLog)
            log.write(message)
        except Exception:
            pass

    def watch_status_message(self, message: str) -> None:
        """React to status message changes."""
        self._log(message)

    def watch_is_testing(self, testing: bool) -> None:
        """Update UI when test state changes."""
        try:
            self.query_one("#test-button", Button).disabled = testing
            self.query_one("#stop-button", Button).disabled = not testing
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "test-button":
            self.run_test()
        elif button_id == "stop-button":
            self.stop_test()
        elif button_id == "history-button":
            self.show_history()
        elif button_id == "quick-button":
            self.run_quick_test()

    def action_run_test(self) -> None:
        """Action: run a speed test."""
        self.run_test()

    def action_show_history(self) -> None:
        """Action: show history screen."""
        self.show_history()

    def action_show_config(self) -> None:
        """Action: show config screen."""
        self.push_screen(ConfigScreen())

    def action_toggle_detail(self) -> None:
        """Action: toggle detail view."""
        self._show_detail = not self._show_detail
        self._log(f"[dim]Detail view: {'ON' if self._show_detail else 'OFF'}[/dim]")

    def run_test(self) -> None:
        """Start a speed test in the background."""
        if self.is_testing:
            return
        self.is_testing = True
        self.status_message = "[yellow]Starting speed test...[/yellow]"
        self._test_task = asyncio.create_task(self._run_test_async())

    def stop_test(self) -> None:
        """Cancel a running test."""
        if self._test_task and not self._test_task.done():
            self._test_task.cancel()
            self.is_testing = False
            self.status_message = "[red]Test cancelled.[/red]"

    def run_quick_test(self) -> None:
        """Run a one-shot quick test and show results."""
        self.run_test()

    async def _run_test_async(self) -> None:
        """Run the speed test asynchronously with progress updates."""

        def progress_callback(stage: str, progress: float) -> None:
            self._progress_stage = stage
            self._progress_value = progress

        self.tester.callback = progress_callback

        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.tester.run_test)

        # Post-test updates
        self.is_testing = False

        if result.error:
            self._log(f"[red]Test failed: {result.error}[/red]")
            self.status_message = f"[red]Error: {result.error}[/red]"
            return

        # Store in history
        self.history.add(result)

        # Update gauges
        try:
            dl_gauge = self.query_one("#dl-gauge", SpeedGauge)
            dl_gauge.set_value(result.download_mbps)
        except Exception:
            pass

        try:
            ul_gauge = self.query_one("#ul-gauge", SpeedGauge)
            ul_gauge.set_value(result.upload_mbps)
        except Exception:
            pass

        try:
            ping_gauge = self.query_one("#ping-gauge", SpeedGauge)
            ping_gauge.set_value(result.ping_ms)
        except Exception:
            pass

        # Update chart
        try:
            chart = self.query_one("#speed-chart", SpeedChart)
            chart.add_point(result.download_mbps, result.upload_mbps)
        except Exception:
            pass

        # Update server info
        try:
            server_info = self.query_one("#server-info", ServerInfoWidget)
            server_info.set_server(
                name=result.server_name,
                location=result.server_location,
                isp=result.isp,
                ip=result.external_ip,
            )
        except Exception:
            pass

        # Log result
        ts = time.strftime("%H:%M:%S", time.localtime(result.timestamp))
        self._log(
            f"[green]✓[/green] [bold]{ts}[/bold] — "
            f"DL: [cyan]{result.download_mbps:.2f}[/cyan] Mbps | "
            f"UL: [magenta]{result.upload_mbps:.2f}[/magenta] Mbps | "
            f"Ping: [yellow]{result.ping_ms:.1f}[/yellow] ms"
        )

        self.status_message = (
            f"[green]Download: {result.download_mbps:.2f} Mbps | "
            f"Upload: {result.upload_mbps:.2f} Mbps | "
            f"Ping: {result.ping_ms:.1f} ms[/green]"
        )

        # Save to file if requested
        if self.output:
            try:
                with open(self.output, "a") as f:
                    f.write(result.to_json() + "\n")
                self._log(f"[dim]Saved to {self.output}[/dim]")
            except IOError as e:
                self._log(f"[red]Could not save: {e}[/red]")

    def show_history(self) -> None:
        """Navigate to history screen."""
        self.push_screen(HistoryScreen(self.history))

    def on_screen_resume(self, screen: Screen) -> None:
        """Refresh when returning from a sub-screen."""
        if isinstance(screen, HistoryScreen):
            self.refresh()
