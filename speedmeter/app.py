"""SpeedMeter Textual TUI Application — cyberpunk internet speed meter."""

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
from textual.widgets import Button, Footer, Header, Label, RichLog, Static

from speedmeter.config import get_default_config
from speedmeter.history import HistoryManager
from speedmeter.tester import NetworkMonitor, SpeedTester, SpeedTestResult
from speedmeter.widgets import (
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_RED,
    NEON_YELLOW,
    TEXT_DIM,
    MonitorDisplay,
    ServerInfoWidget,
    SpeedChart,
    SpeedGauge,
    SystemStatusWidget,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Screens
# =============================================================================


class TestResultCard(Static):
    """A cyberpunk-style card displaying a single speed test result."""

    def __init__(self, result: SpeedTestResult, precision: int = 2):
        super().__init__()
        self.result = result
        self.precision = precision

    def render(self):
        """Render the result card."""
        r = self.result
        if r.error:
            return Panel(
                Text(f"ERROR: {r.error}", style=f"bold {NEON_RED}"),
                title="[bold]TEST FAILED[/bold]",
                border_style=NEON_RED,
            )

        grid = Table.grid(padding=(0, 2))
        grid.add_column(style=f"bold {TEXT_DIM}")
        grid.add_column()

        dl_color = NEON_GREEN if r.download_mbps >= 50 else NEON_YELLOW if r.download_mbps >= 10 else NEON_RED
        ul_color = NEON_GREEN if r.upload_mbps >= 20 else NEON_YELLOW if r.upload_mbps >= 5 else NEON_RED

        grid.add_row(
            Text("DOWNLOAD:", style=f"bold {TEXT_DIM}"),
            Text(f"{r.download_mbps:.{self.precision}f} Mbps", style=f"bold {dl_color}"),
        )
        grid.add_row(
            Text("UPLOAD:", style=f"bold {TEXT_DIM}"),
            Text(f"{r.upload_mbps:.{self.precision}f} Mbps", style=f"bold {ul_color}"),
        )
        grid.add_row(
            Text("PING:", style=f"bold {TEXT_DIM}"),
            Text(f"{r.ping_ms:.1f} ms", style=NEON_CYAN),
        )
        if r.jitter_ms > 0:
            grid.add_row(
                Text("JITTER:", style=f"bold {TEXT_DIM}"),
                Text(f"{r.jitter_ms:.1f} ms", style=f"dim {NEON_CYAN}"),
            )
        grid.add_row(
            Text("SERVER:", style=f"bold {TEXT_DIM}"),
            Text(f"{r.server_name}", style=NEON_CYAN),
        )
        grid.add_row(
            Text("DURATION:", style=f"bold {TEXT_DIM}"),
            Text(f"{r.duration_seconds:.1f}s", style=TEXT_DIM),
        )

        ts = time.strftime("%H:%M:%S", time.localtime(r.timestamp))
        return Panel(
            grid,
            title=f"[bold]{ts}[/bold]",
            border_style=NEON_CYAN,
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
            container.mount(Static(f"[dim {TEXT_DIM}]No tests recorded yet.[/dim]"))
        for result in results:
            container.mount(TestResultCard(result))


class ConfigScreen(Screen):
    """Screen for viewing/editing configuration."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("[bold]CONFIGURATION[/bold]", id="config-title"),
            Static("Configuration UI is under construction."),
            id="config-container",
        )
        yield Footer()


# =============================================================================
# Main Application
# =============================================================================


class SpeedMeterApp(App):
    """Cyberpunk-styled SpeedMeter TUI with continuous monitoring."""

    # CSS theme — cyberpunk neon palette, no f-string interpolation needed
    CSS = """
    Screen {
        background: #0a0e14;
    }

    Header {
        background: #0d1117;
        color: #00ff41;
        text-style: bold;
    }

    Footer {
        background: #0d1117;
        color: #565f89;
    }

    /* Main layout */
    #main-container {
        layout: grid;
        grid-size: 2;
        grid-gutter: 0;
        padding: 0 1;
        height: 100%;
    }

    #left-column {
        height: 100%;
    }

    #right-column {
        height: 100%;
    }

    /* Gauges row */
    #gauges {
        height: auto;
        margin: 0;
    }

    SpeedGauge {
        width: 1fr;
        height: auto;
        min-height: 8;
    }

    /* Monitor section */
    #monitor-section {
        height: auto;
        margin: 0 0 1 0;
    }

    MonitorDisplay {
        height: auto;
        min-height: 8;
    }

    /* Chart */
    SpeedChart {
        height: auto;
        min-height: 14;
    }

    /* Info panels */
    ServerInfoWidget, SystemStatusWidget {
        height: auto;
        min-height: 6;
    }

    /* Bottom panel */
    #bottom-panel {
        height: auto;
        max-height: 10;
    }

    /* Status log */
    RichLog {
        background: #0d1117;
        border: solid #565f89;
        height: 100%;
        max-height: 4;
    }

    /* Controls */
    #controls {
        height: 3;
        align: center middle;
        padding: 0 1;
    }

    Button {
        margin: 0 1;
        min-width: 14;
    }

    Button:hover {
        text-style: bold;
        background: #00ff41;
        color: #0a0e14;
    }

    #test-button {
        background: #00ff41;
        color: #0a0e14;
        text-style: bold;
    }

    #monitor-button {
        background: #00d4ff;
        color: #0a0e14;
        text-style: bold;
    }

    #stop-button {
        background: #ff0044;
        color: #0a0e14;
        text-style: bold;
    }

    #history-button {
        background: #0d1117;
        color: #00d4ff;
        border: solid #565f89;
    }

    /* State classes */
    .error-text {
        color: #ff0044;
    }
    .success-text {
        color: #00ff41;
    }
    .info-text {
        color: #00d4ff;
    }

    /* History scrolling */
    #history-container {
        overflow-y: scroll;
        height: 100%;
    }

    #history-container TestResultCard {
        margin: 0 0 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "run_test", "Run Test", show=True),
        Binding("m", "toggle_monitor", "Monitor", show=True),
        Binding("s", "show_history", "History", show=True),
        Binding("c", "show_config", "Config", show=True),
        Binding("d", "toggle_detail", "Detail", show=True),
        Binding("space", "run_test", "Run", show=True),
    ]

    # Reactive properties
    is_testing = reactive(False)
    is_monitoring = reactive(False)
    status_message = reactive("Ready. [bold]Space[/] = Test  [bold]M[/] = Monitor  [bold]Q[/] = Quit")

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        server_id: Optional[int] = None,
        output: Optional[str] = None,
        start_monitor: bool = False,
    ):
        super().__init__()
        self.config = config or get_default_config()
        self.server_id = server_id
        self.output = output
        self.start_monitor = start_monitor
        self.history = HistoryManager(
            max_size=self.config.get("app", {}).get("history_size", 50),
        )
        self.tester = SpeedTester(
            server_id=self.server_id,
            timeout=self.config.get("app", {}).get("timeout", 30),
        )
        self.monitor = NetworkMonitor(
            callback=self._on_monitor_data,
            interval=self.config.get("app", {}).get("refresh_interval", 1),
        )
        self._test_task: Optional[asyncio.Task] = None
        self._progress_value = 0.0
        self._progress_stage = ""
        self._show_detail = False

    def compose(self) -> ComposeResult:
        """Create the application layout."""
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical(id="left-column"):
                # Speed gauges row
                with Horizontal(id="gauges"):
                    yield SpeedGauge(
                        label="DOWNLOAD",
                        unit="Mbps",
                        max_value=1000.0,
                        accent_color=NEON_CYAN,
                        id="dl-gauge",
                    )
                    yield SpeedGauge(
                        label="UPLOAD",
                        unit="Mbps",
                        max_value=500.0,
                        accent_color=NEON_MAGENTA,
                        id="ul-gauge",
                    )
                    yield SpeedGauge(
                        label="PING",
                        unit="ms",
                        max_value=200.0,
                        danger_threshold=100.0,
                        warning_threshold=50.0,
                        accent_color=NEON_YELLOW,
                        id="ping-gauge",
                    )
                # Monitor display
                with Vertical(id="monitor-section"):
                    yield MonitorDisplay(id="monitor-display")
                # Speed history chart
                yield SpeedChart(max_points=30, label="SPEED HISTORY", id="speed-chart")
            with Vertical(id="right-column"):
                yield ServerInfoWidget(id="server-info")
                yield SystemStatusWidget(id="sys-status")
            # Bottom panel
            with Vertical(id="bottom-panel"):
                yield RichLog(id="status-log", highlight=True, markup=True, max_lines=5)
                with Horizontal(id="controls"):
                    yield Button("RUN TEST [Space]", id="test-button", variant="success")
                    yield Button("MONITOR [M]", id="monitor-button", variant="primary")
                    yield Button("STOP", id="stop-button", variant="error", disabled=True)
                    yield Button("HISTORY [S]", id="history-button")
        yield Footer(id="app-footer")

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#status-log", RichLog).write(
            "[bold #00ff41]SPEEDMETER v1.1.0[/bold #00ff41] — Cyberpunk Internet Speed Meter"
        )
        self.query_one("#status-log", RichLog).write(
            "[dim #565f89]Space[/] = Run Test  [dim #565f89]M[/] = Toggle Monitor  [dim #565f89]Q[/] = Quit"
        )
        self.set_interval(5, self._update_system_stats)
        self.set_interval(1, self._tick_animations)

        # Auto-start monitor if requested (--monitor flag)
        if self.start_monitor:
            self.toggle_monitor()

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

    def watch_is_monitoring(self, monitoring: bool) -> None:
        """Update UI when monitor state changes."""
        try:
            btn = self.query_one("#monitor-button", Button)
            btn.label = "STOP MONITOR [M]" if monitoring else "MONITOR [M]"
            btn.variant = "error" if monitoring else "primary"
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "test-button":
            self.run_test()
        elif button_id == "monitor-button":
            self.toggle_monitor()
        elif button_id == "stop-button":
            self.stop_test()
        elif button_id == "history-button":
            self.show_history()

    # =========================================================================
    # Actions
    # =========================================================================

    def action_run_test(self) -> None:
        """Action: run a speed test."""
        self.run_test()

    def action_toggle_monitor(self) -> None:
        """Action: toggle continuous monitoring."""
        self.toggle_monitor()

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

    # =========================================================================
    # Speed Test
    # =========================================================================

    def run_test(self) -> None:
        """Start a speed test in the background."""
        if self.is_testing:
            return
        self.is_testing = True
        self.status_message = "[#ffd700]Starting speed test...[/#ffd700]"
        self._test_task = asyncio.create_task(self._run_test_async())

    def stop_test(self) -> None:
        """Cancel a running test."""
        if self._test_task and not self._test_task.done():
            self._test_task.cancel()
            self.is_testing = False
            self.status_message = "[#ff0044]Test cancelled.[/#ff0044]"

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
            self._log(f"[#ff0044]Test failed: {result.error}[/#ff0044]")
            self.status_message = f"[#ff0044]Error: {result.error}[/#ff0044]"
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
            "[#00ff41]\u2713[/#00ff41] [bold]"
            + ts
            + "[/bold] \u2014 "
            + f"DL: [#00d4ff]{result.download_mbps:.2f}[/#00d4ff] Mbps | "
            + f"UL: [#ff00ff]{result.upload_mbps:.2f}[/#ff00ff] Mbps | "
            + f"Ping: [#ffd700]{result.ping_ms:.1f}[/#ffd700] ms"
        )

        self.status_message = (
            f"[#00ff41]Download: {result.download_mbps:.2f} Mbps | "
            f"Upload: {result.upload_mbps:.2f} Mbps | "
            f"Ping: {result.ping_ms:.1f} ms[/#00ff41]"
        )

        # Save to file if requested
        if self.output:
            try:
                with open(self.output, "a") as f:
                    f.write(result.to_json() + "\n")
                self._log(f"[dim]Saved to {self.output}[/dim]")
            except IOError as e:
                self._log(f"[#ff0044]Could not save: {e}[/#ff0044]")

    # =========================================================================
    # Continuous Monitoring
    # =========================================================================

    def toggle_monitor(self) -> None:
        """Toggle continuous network monitoring on/off."""
        if self.is_monitoring:
            self._stop_monitor()
        else:
            self._start_monitor()

    def _start_monitor(self) -> None:
        """Start continuous network monitoring."""
        self.monitor.start()
        self.is_monitoring = True
        self.status_message = "[#00ff41]Monitoring started — tracking live network traffic[/#00ff41]"
        self._log("[#00ff41]LIVE MONITOR: tracking network traffic in real-time[/#00ff41]")

    def _stop_monitor(self) -> None:
        """Stop continuous network monitoring."""
        self.monitor.stop()
        self.is_monitoring = False
        self.status_message = "[#ffd700]Monitoring stopped[/#ffd700]"
        self._log("[#ffd700]LIVE MONITOR: stopped[/#ffd700]")

    def _on_monitor_data(self, dl_mbps: float, ul_mbps: float) -> None:
        """Called by NetworkMonitor each tick with live speed data."""
        # This runs in a background thread — use call_from_thread for UI updates
        try:
            self.call_from_thread(self._update_monitor_display, dl_mbps, ul_mbps)
        except Exception:
            pass

    def _update_monitor_display(self, dl_mbps: float, ul_mbps: float) -> None:
        """Update the monitor display widget (runs in event loop thread)."""
        try:
            display = self.query_one("#monitor-display", MonitorDisplay)
            display.update_speed(dl_mbps, ul_mbps)

            # Also update gauges to reflect live traffic
            try:
                dl_gauge = self.query_one("#dl-gauge", SpeedGauge)
                dl_gauge.set_value(dl_mbps)
            except Exception:
                pass
            try:
                ul_gauge = self.query_one("#ul-gauge", SpeedGauge)
                ul_gauge.set_value(ul_mbps)
            except Exception:
                pass
        except Exception:
            pass

    def show_history(self) -> None:
        """Navigate to history screen."""
        self.push_screen(HistoryScreen(self.history))

    def on_screen_resume(self, screen: Screen) -> None:
        """Refresh when returning from a sub-screen."""
        if isinstance(screen, HistoryScreen):
            self.refresh()
