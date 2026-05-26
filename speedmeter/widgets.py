"""Cyberpunk-styled Textual widgets for the SpeedMeter TUI."""

import time

from rich.console import RenderableType
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

# Cyberpunk neon color palette
NEON_GREEN = "#00ff41"
NEON_CYAN = "#00d4ff"
NEON_MAGENTA = "#ff00ff"
NEON_PINK = "#ff0080"
NEON_YELLOW = "#ffd700"
NEON_RED = "#ff0044"
DARK_BG = "#0a0e14"
SURFACE_BG = "#0d1117"
HUD_BORDER = "#1a1f2e"
TEXT_COLOR = "#c0caf5"
TEXT_DIM = "#565f89"


def _neon_style(color: str, bold: bool = True) -> str:
    """Create a neon-styled text string with optional bold."""
    return f"bold {color}" if bold else color


class SpeedGauge(Static):
    """A cyberpunk-styled speed gauge with neon glow appearance."""

    def __init__(
        self,
        label: str = "SPEED",
        unit: str = "Mbps",
        max_value: float = 1000.0,
        warning_threshold: float = 10.0,
        danger_threshold: float = 5.0,
        accent_color: str = NEON_CYAN,
    ):
        super().__init__()
        self.label = label.upper()
        self.unit = unit
        self.max_value = max_value
        self.warning_threshold = warning_threshold
        self.danger_threshold = danger_threshold
        self.accent_color = accent_color
        self.current_value = 0.0
        self.animate_to = 0.0
        self.animation_progress = 1.0

    def set_value(self, value: float, animate: bool = True) -> None:
        """Set the current value of the gauge."""
        self.animate_to = value
        if not animate:
            self.current_value = value
        self.refresh()

    def render(self) -> RenderableType:
        """Render the gauge with cyberpunk styling."""
        value = self.current_value + (self.animate_to - self.current_value) * self.animation_progress
        if self.animation_progress >= 1.0:
            self.current_value = self.animate_to
        else:
            self.animation_progress = min(1.0, self.animation_progress + 0.1)

        clamped = max(0, min(value, self.max_value))
        fraction = clamped / self.max_value if self.max_value > 0 else 0

        # Pick color based on value thresholds
        if value <= self.danger_threshold:
            bar_color = NEON_RED
        elif value <= self.warning_threshold:
            bar_color = NEON_YELLOW
        else:
            bar_color = self.accent_color

        # Build the visual
        bar = ProgressBar(
            total=self.max_value,
            completed=clamped,
            width=36,
            complete_style=Style(color=bar_color, bgcolor=bar_color),
            finished_style=Style(color=bar_color),
        )

        # Value text with glow style
        if value >= 1000:
            display_val = f"{value / 1000:.2f} Gbps"
        elif value >= 1:
            display_val = f"{value:.2f} {self.unit}"
        else:
            display_val = f"{value:.3f} {self.unit}"

        value_text = Text(f" {display_val} ", style=f"bold {bar_color} on {SURFACE_BG}")

        # HUD-style dial indicator
        dial_pos = min(int(fraction * 28), 28)
        dial = " " * dial_pos + "\u25b2" + " " * (28 - dial_pos)
        dial_text = Text(f"[{dial}]", style=f"dim {bar_color}")

        # Label header
        header = Text.assemble(
            (f" {self.label} ", f"bold white on {bar_color}"),
            (f" [{self.unit}]", f"dim {bar_color}"),
        )

        # Build inner content
        grid = Table.grid(padding=(0, 0))
        grid.add_column(justify="center")
        grid.add_row(Panel(header, style=Style(bgcolor=SURFACE_BG), border_style=Style(color=HUD_BORDER)))
        grid.add_row(value_text)
        grid.add_row(bar)
        grid.add_row(dial_text)
        grid.add_row(
            Text(
                f"0 {self.unit}" + " " * 20 + f"{self.max_value:.0f} {self.unit}",
                style=f"dim {TEXT_DIM}",
            )
        )

        return Panel(
            grid,
            border_style=Style(color=bar_color),
            padding=(0, 0),
        )


class SpeedChart(Static):
    """A cyberpunk sparkline chart for speed history."""

    def __init__(self, max_points: int = 30, label: str = "SPEED HISTORY"):
        super().__init__()
        self.max_points = max_points
        self.label = label.upper()
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

    def render(self) -> RenderableType:
        """Render the chart with cyberpunk sparklines."""
        if not self.download_history:
            return Panel(
                Text("NO DATA \u2014 run a speed test to populate the chart.", style=f"dim {TEXT_DIM}"),
                title=self.label,
                border_style=Style(color=NEON_CYAN),
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
                    line_chars.append("\u2588")
                elif dl >= threshold:
                    line_chars.append("\u2580")
                elif ul >= threshold:
                    line_chars.append("\u2584")
                else:
                    line_chars.append("\u00b7")
            lines.append("".join(line_chars))

        chart_panel = "\n".join(lines)

        # Legend with max/avg stats
        max_dl = max(self.download_history) if self.download_history else 0
        max_ul = max(self.upload_history) if self.upload_history else 0
        avg_dl = sum(self.download_history) / len(self.download_history) if self.download_history else 0
        avg_ul = sum(self.upload_history) / len(self.upload_history) if self.upload_history else 0

        info = Table.grid(padding=(0, 2))
        info.add_column()
        info.add_column()
        info.add_row(
            Text(f"\u2580 DOWNLOAD  Max: {max_dl:.1f}  Avg: {avg_dl:.1f}", style=NEON_CYAN),
            Text(f"\u2584 UPLOAD    Max: {max_ul:.1f}  Avg: {avg_ul:.1f}", style=NEON_MAGENTA),
        )

        return Panel(
            Text(chart_panel),
            title=f"[{self.label}]",
            border_style=Style(color=NEON_CYAN),
            subtitle=f"[dim]Last {len(self.download_history)} tests[/dim]",
        )


class SystemStatusWidget(Static):
    """Cyberpunk system resource monitor widget."""

    def render(self) -> RenderableType:
        """Render system status with neon-themed display."""
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            net = psutil.net_io_counters()
            uptime_seconds = int(time.time() - psutil.boot_time())
        except ImportError:
            cpu = mem_percent = 0
            net = None
            uptime_seconds = 0
        else:
            mem_percent = mem.percent if hasattr(mem, "percent") else 0

        uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

        table = Table.grid(padding=(0, 2))
        table.add_column(style=f"bold {TEXT_DIM}")
        table.add_column()

        cpu_color = NEON_GREEN if cpu < 50 else NEON_YELLOW if cpu < 80 else NEON_RED
        mem_color = NEON_GREEN if mem_percent < 50 else NEON_YELLOW if mem_percent < 80 else NEON_RED

        table.add_row("CPU:", Text(f"{cpu:.1f}%", style=f"bold {cpu_color}"))
        if mem_percent > 0:
            table.add_row("MEM:", Text(f"{mem_percent:.1f}%", style=f"bold {mem_color}"))
        table.add_row("UP:", Text(uptime_str, style=f"bold {NEON_CYAN}"))
        if net:
            net_recv = net.bytes_recv / 1024 / 1024 / 1024
            net_sent = net.bytes_sent / 1024 / 1024 / 1024
            table.add_row(
                "NET:",
                Text(
                    f"\u2193 {net_recv:.1f} GB  \u2191 {net_sent:.1f} GB",
                    style=f"dim {NEON_CYAN}",
                ),
            )

        return Panel(
            table,
            title="[bold]SYS[/bold]",
            border_style=Style(color=NEON_GREEN),
        )


class ServerInfoWidget(Static):
    """Cyberpunk server info display widget."""

    def __init__(self):
        super().__init__()
        self.server_name = "\u2014"
        self.server_location = "\u2014"
        self.isp = "\u2014"
        self.ip = "\u2014"

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

    def render(self) -> RenderableType:
        """Render server info with neon styling."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style=f"bold {TEXT_DIM}")
        table.add_column()
        table.add_row("SRV:", Text(self.server_name, style=NEON_CYAN))
        table.add_row("LOC:", Text(self.server_location, style=f"dim {TEXT_COLOR}"))
        table.add_row("ISP:", Text(self.isp, style=f"dim {TEXT_COLOR}"))
        table.add_row("IP:", Text(self.ip, style=f"dim {NEON_YELLOW}"))
        return Panel(
            table,
            title="[bold]CONNECTION[/bold]",
            border_style=Style(color=NEON_CYAN),
        )


class MonitorDisplay(Static):
    """Widget for live network traffic monitoring display."""

    def __init__(self):
        super().__init__()
        self.download_mbps = 0.0
        self.upload_mbps = 0.0
        self.peak_download = 0.0
        self.peak_upload = 0.0
        self._total_dl = 0.0
        self._total_ul = 0.0
        self._samples = 0

    def update_speed(self, dl_mbps: float, ul_mbps: float) -> None:
        """Update live speed readings."""
        self.download_mbps = dl_mbps
        self.upload_mbps = ul_mbps
        self.peak_download = max(self.peak_download, dl_mbps)
        self.peak_upload = max(self.peak_upload, ul_mbps)
        self._total_dl += dl_mbps
        self._total_ul += ul_mbps
        self._samples += 1
        self.refresh()

    def reset(self) -> None:
        """Reset all readings."""
        self.download_mbps = 0.0
        self.upload_mbps = 0.0
        self.peak_download = 0.0
        self.peak_upload = 0.0
        self._total_dl = 0.0
        self._total_ul = 0.0
        self._samples = 0
        self.refresh()

    def render(self) -> RenderableType:
        """Render the monitor display."""
        avg_dl = self._total_dl / self._samples if self._samples > 0 else 0.0
        avg_ul = self._total_ul / self._samples if self._samples > 0 else 0.0

        table = Table.grid(padding=(0, 2))
        table.add_column(justify="right", style=f"bold {TEXT_DIM}")
        table.add_column(justify="right")
        table.add_column(style=f"bold {TEXT_DIM}")
        table.add_column(justify="right")

        def fmt_speed(val: float) -> str:
            if val >= 1000:
                return f"{val / 1000:.2f} Gbps"
            return f"{val:.3f} Mbps"

        dl_color = NEON_GREEN if self.download_mbps > 1 else NEON_CYAN if self.download_mbps > 0.1 else TEXT_DIM
        ul_color = NEON_MAGENTA if self.upload_mbps > 1 else NEON_CYAN if self.upload_mbps > 0.1 else TEXT_DIM

        table.add_row(
            Text("\u2193 LIVE DL:", style=f"bold {NEON_CYAN}"),
            Text(fmt_speed(self.download_mbps), style=f"bold {dl_color}"),
            Text("PEAK:", style=f"dim {TEXT_DIM}"),
            Text(fmt_speed(self.peak_download), style=f"dim {NEON_GREEN}"),
        )
        table.add_row(
            Text("\u2191 LIVE UL:", style=f"bold {NEON_MAGENTA}"),
            Text(fmt_speed(self.upload_mbps), style=f"bold {ul_color}"),
            Text("AVG:", style=f"dim {TEXT_DIM}"),
            Text(f"{avg_dl:.3f} / {avg_ul:.3f} Mbps", style=f"dim {TEXT_DIM}"),
        )

        # Build a mini sparkline for current speeds
        bar_width = 30
        dl_bar = int((self.download_mbps / max(self.peak_download, 1)) * bar_width) if self.peak_download > 0 else 0
        ul_bar = int((self.upload_mbps / max(self.peak_upload, 1)) * bar_width) if self.peak_upload > 0 else 0
        dl_bar = min(dl_bar, bar_width)
        ul_bar = min(ul_bar, bar_width)

        block = "\u2588"
        dot = "\u2591"
        sparkline = Text(
            f"\u2193 {block * dl_bar}{dot * (bar_width - dl_bar)}",
            style=NEON_CYAN,
        )
        sparkline.append(f"\n\u2191 {block * ul_bar}{dot * (bar_width - ul_bar)}", style=NEON_MAGENTA)

        return Panel(
            Text.assemble(
                table,
                Text(),
                sparkline,
            ),
            title="[bold]LIVE MONITOR[/bold]",
            border_style=Style(color=NEON_GREEN),
        )
