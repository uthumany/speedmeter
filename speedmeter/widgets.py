"""Custom Textual widgets for the SpeedMeter TUI."""

import time

from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text
from textual.app import RenderableType as TextualRenderableType
from textual.widgets import Static


class SpeedGauge(Static):
    """A widget that renders a speed gauge / dial using Rich renderables."""

    def __init__(
        self,
        label: str = "Speed",
        unit: str = "Mbps",
        max_value: float = 1000.0,
        warning_threshold: float = 10.0,
        danger_threshold: float = 5.0,
    ):
        super().__init__()
        self.label = label
        self.unit = unit
        self.max_value = max_value
        self.warning_threshold = warning_threshold
        self.danger_threshold = danger_threshold
        self.current_value = 0.0
        self.animate_to = 0.0
        self.animation_progress = 1.0

    def set_value(self, value: float, animate: bool = True) -> None:
        """Set the current value of the gauge."""
        self.animate_to = value
        if not animate:
            self.current_value = value
        self.refresh()

    def render(self) -> TextualRenderableType:
        """Render the gauge."""
        value = self.current_value + (self.animate_to - self.current_value) * self.animation_progress
        if self.animation_progress >= 1.0:
            # Animation complete — snap current_value so next set_value animates from here
            self.current_value = self.animate_to
        else:
            self.animation_progress = min(1.0, self.animation_progress + 0.1)

        clamped = max(0, min(value, self.max_value))

        # Color based on thresholds
        if value <= self.danger_threshold:
            bar_color = "red"
        elif value <= self.warning_threshold:
            bar_color = "yellow"
        else:
            bar_color = "green"

        # Build the visual
        bar = ProgressBar(
            total=self.max_value,
            completed=clamped,
            width=40,
            complete_style=bar_color,
        )

        # Value text
        if value >= 1000:
            display_val = f"{value / 1000:.2f} Gbps"
        else:
            display_val = f"{value:.2f} {self.unit}"

        value_text = Text(display_val, style=f"bold {bar_color}")

        grid = Table.grid(padding=(0, 1))
        grid.add_column(justify="center")
        grid.add_row(
            Panel(
                Text.assemble(
                    (f" {self.label} ", f"bold white on {bar_color}"),
                ),
                style=f"dim {bar_color}",
            )
        )
        grid.add_row(value_text)
        grid.add_row(bar)
        grid.add_row(Text(f"0 {self.unit}" + " " * 25 + f"{self.max_value:.0f} {self.unit}", style="dim"))

        return Panel(grid, border_style=bar_color)


class SpeedChart(Static):
    """A widget that renders a sparkline-style speed chart."""

    def __init__(self, max_points: int = 30, label: str = "Speed History"):
        super().__init__()
        self.max_points = max_points
        self.label = label
        self.download_history: list[float] = []
        self.upload_history: list[float] = []

    def add_point(self, download: float, upload: float) -> None:
        """Add a data point (download, upload in Mbps)."""
        self.download_history.append(download)
        self.upload_history.append(upload)
        if len(self.download_history) > self.max_points:
            self.download_history.pop(0)
        if len(self.upload_history) > self.max_points:
            self.upload_history.pop(0)
        self.refresh()

    def render(self) -> TextualRenderableType:
        """Render the chart."""
        if not self.download_history:
            return Panel(
                Text("No data yet — run a speed test to populate the chart.", style="dim"),
                title=self.label,
                border_style="blue",
            )

        max_val = max(
            max(self.download_history) if self.download_history else 1,
            max(self.upload_history) if self.upload_history else 1,
            1,
        )
        height = 8
        width = len(self.download_history)
        if width < 2:
            width = 2

        # Build ASCII bar chart
        lines = []
        for row in range(height - 1, -1, -1):
            threshold = (row / (height - 1)) * max_val if height > 1 else max_val
            line_chars = []
            for i in range(width):
                dl = self.download_history[i] if i < len(self.download_history) else 0
                ul = self.upload_history[i] if i < len(self.upload_history) else 0
                if dl >= threshold and ul >= threshold:
                    line_chars.append("█")
                elif dl >= threshold:
                    line_chars.append("▀")
                elif ul >= threshold:
                    line_chars.append("▄")
                else:
                    line_chars.append("·")
            lines.append("".join(line_chars))

        chart_panel = "\n".join(lines)

        # Legend
        max_dl = max(self.download_history) if self.download_history else 0
        max_ul = max(self.upload_history) if self.upload_history else 0
        avg_dl = sum(self.download_history) / len(self.download_history) if self.download_history else 0
        avg_ul = sum(self.upload_history) / len(self.upload_history) if self.upload_history else 0

        info = Table.grid(padding=(0, 2))
        info.add_column()
        info.add_column()
        info.add_row(
            Text(f"▀ Download  Max: {max_dl:.1f}  Avg: {avg_dl:.1f}", style="cyan"),
            Text(f"▄ Upload    Max: {max_ul:.1f}  Avg: {avg_ul:.1f}", style="magenta"),
        )

        return Panel(
            Text(chart_panel),
            title=self.label,
            border_style="blue",
            subtitle=f"Showing last {len(self.download_history)} tests",
        )


class SystemStatusWidget(Static):
    """Widget displaying system resource usage."""

    def render(self) -> TextualRenderableType:
        """Render system status."""
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            net = psutil.net_io_counters()
            uptime_seconds = int(time.time() - psutil.boot_time())
        except ImportError:
            cpu = mem = 0
            net = None
            uptime_seconds = 0

        uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        cpu_color = "green" if cpu < 50 else "yellow" if cpu < 80 else "red"
        mem_color = (
            "green"
            if mem.percent < 50
            else "yellow"
            if mem.percent < 80
            else "red"
            if hasattr(mem, "percent")
            else "white"
        )

        table.add_row("CPU:", Text(f"{cpu:.1f}%", style=cpu_color))
        if hasattr(mem, "percent"):
            table.add_row("Memory:", Text(f"{mem.percent:.1f}%", style=mem_color))
        table.add_row("Uptime:", uptime_str)
        if net:
            table.add_row(
                "Network:",
                f"↓ {net.bytes_recv / 1024 / 1024 / 1024:.1f} GB  ↑ {net.bytes_sent / 1024 / 1024 / 1024:.1f} GB",
            )

        return Panel(table, title="System", border_style="green")


class ServerInfoWidget(Static):
    """Widget displaying current speed test server info."""

    def __init__(self):
        super().__init__()
        self.server_name = "—"
        self.server_location = "—"
        self.isp = "—"
        self.ip = "—"

    def set_server(self, name: str = "", location: str = "", isp: str = "", ip: str = "") -> None:
        """Update server information."""
        if name:
            self.server_name = name
        if location:
            self.server_location = location
        if isp:
            self.isp = isp
        if ip:
            self.ip = ip
        self.refresh()

    def render(self) -> TextualRenderableType:
        """Render server info panel."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()
        table.add_row("Server:", self.server_name)
        table.add_row("Location:", self.server_location)
        table.add_row("ISP:", self.isp)
        table.add_row("IP:", self.ip)
        return Panel(table, title="Connection", border_style="cyan")
