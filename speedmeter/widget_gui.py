"""Lightweight desktop GUI widget for SpeedMeter — live speed display.

This module provides a small, always-on-top tkinter window that shows
real-time download and upload speed readings. It can be:

1. Launched standalone: python -m speedmeter.widget_gui
2. Launched via CLI: speedmeter --widget
3. Embedded into the TUI workflow (reads from shared state)
"""

import sys
import time

try:
    import tkinter as tk

    HAS_TK = True
except ImportError:
    HAS_TK = False

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[assignment]


# Colors
BG_COLOR = "#0a0e14"
FG_DL = "#00d4ff"
FG_UL = "#ff00ff"
FG_LABEL = "#565f89"
FG_TEXT = "#c0caf5"
FG_GREEN = "#00ff41"
FG_RED = "#ff0044"
FG_YELLOW = "#ffd700"

WINDOW_WIDTH = 320
WINDOW_HEIGHT = 120


class SpeedWidget:
    """Tkinter-based always-on-top speed monitor widget."""

    def __init__(self, tk_root: tk.Tk):
        self.root = tk_root
        self.root.title("SpeedMeter")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        # Remove window decorations if possible (platform-dependent)
        self.root.overrideredirect(False)

        # Bind close to Escape
        self.root.bind("<Escape>", lambda e: self.root.quit())

        # Monitor state
        self.dl_mbps = 0.0
        self.ul_mbps = 0.0
        self.peak_dl = 0.0
        self.peak_ul = 0.0
        self.monitoring = True
        self._last_recv = 0
        self._last_sent = 0
        self._last_time = time.time()

        # Build UI
        self._build_ui()

        # Start monitoring
        self._update_loop()

    def _build_ui(self) -> None:
        """Build the widget UI components."""
        # Title
        title_frame = tk.Frame(self.root, bg=BG_COLOR)
        title_frame.pack(fill="x", padx=10, pady=(8, 2))

        title_label = tk.Label(
            title_frame,
            text="SPEEDMETER",
            fg=FG_GREEN,
            bg=BG_COLOR,
            font=("Consolas", 10, "bold"),
        )
        title_label.pack(side="left")

        status_label = tk.Label(
            title_frame,
            text="LIVE",
            fg=FG_GREEN,
            bg=BG_COLOR,
            font=("Consolas", 8),
        )
        status_label.pack(side="right")

        # Separator
        sep = tk.Frame(self.root, height=1, bg="#1a1f2e")
        sep.pack(fill="x", padx=10, pady=(0, 6))

        # Download row
        dl_frame = tk.Frame(self.root, bg=BG_COLOR)
        dl_frame.pack(fill="x", padx=10, pady=(0, 2))

        dl_label = tk.Label(
            dl_frame,
            text="\u2193 DOWNLOAD",
            fg=FG_LABEL,
            bg=BG_COLOR,
            font=("Consolas", 8),
            width=12,
            anchor="w",
        )
        dl_label.pack(side="left")

        self.dl_value = tk.Label(
            dl_frame,
            text="0.000 Mbps",
            fg=FG_DL,
            bg=BG_COLOR,
            font=("Consolas", 11, "bold"),
            anchor="e",
        )
        self.dl_value.pack(side="right")

        # Upload row
        ul_frame = tk.Frame(self.root, bg=BG_COLOR)
        ul_frame.pack(fill="x", padx=10, pady=(0, 2))

        ul_label = tk.Label(
            ul_frame,
            text="\u2191 UPLOAD",
            fg=FG_LABEL,
            bg=BG_COLOR,
            font=("Consolas", 8),
            width=12,
            anchor="w",
        )
        ul_label.pack(side="left")

        self.ul_value = tk.Label(
            ul_frame,
            text="0.000 Mbps",
            fg=FG_UL,
            bg=BG_COLOR,
            font=("Consolas", 11, "bold"),
            anchor="e",
        )
        self.ul_value.pack(side="right")

        # Peak / status row
        peak_frame = tk.Frame(self.root, bg=BG_COLOR)
        peak_frame.pack(fill="x", padx=10, pady=(4, 0))

        self.peak_label = tk.Label(
            peak_frame,
            text="Peak: 0.000 / 0.000 Mbps",
            fg=FG_LABEL,
            bg=BG_COLOR,
            font=("Consolas", 7),
        )
        self.peak_label.pack(side="left")

        self.connection_label = tk.Label(
            peak_frame,
            text="\u25cf Monitoring",
            fg=FG_GREEN,
            bg=BG_COLOR,
            font=("Consolas", 7),
        )
        self.connection_label.pack(side="right")

        # Quit hint
        hint = tk.Label(
            self.root,
            text="Press ESC to close",
            fg=FG_LABEL,
            bg=BG_COLOR,
            font=("Consolas", 7),
        )
        hint.pack(side="bottom", pady=(0, 4))

    def _read_network_speed(self) -> tuple[float, float]:
        """Read current network speed using psutil.

        Returns:
            Tuple of (download_mbps, upload_mbps)
        """
        if psutil is None:
            return 0.0, 0.0

        try:
            counters = psutil.net_io_counters()
            now = time.time()
            dt = now - self._last_time

            if dt <= 0 or self._last_recv <= 0 or self._last_sent <= 0:
                self._last_recv = counters.bytes_recv
                self._last_sent = counters.bytes_sent
                self._last_time = now
                return 0.0, 0.0

            dl_bps = (counters.bytes_recv - self._last_recv) * 8 / dt
            ul_bps = (counters.bytes_sent - self._last_sent) * 8 / dt

            self._last_recv = counters.bytes_recv
            self._last_sent = counters.bytes_sent
            self._last_time = now

            dl_mbps = max(0.0, dl_bps / 1_000_000)
            ul_mbps = max(0.0, ul_bps / 1_000_000)

            return dl_mbps, ul_mbps

        except Exception:
            return 0.0, 0.0

    def _format_speed(self, val: float) -> str:
        """Format speed value for display."""
        if val >= 1000:
            return f"{val / 1000:.2f} Gbps"
        elif val >= 1:
            return f"{val:.2f} Mbps"
        elif val >= 0.001:
            return f"{val:.3f} Mbps"
        else:
            return "0.000 Mbps"

    def _update_loop(self) -> None:
        """Periodic update loop — reads speeds and updates display."""
        if not self.monitoring:
            return

        dl, ul = self._read_network_speed()
        self.dl_mbps = dl
        self.ul_mbps = ul
        self.peak_dl = max(self.peak_dl, dl)
        self.peak_ul = max(self.peak_ul, ul)

        # Update labels
        self.dl_value.config(text=self._format_speed(dl))
        self.ul_value.config(text=self._format_speed(ul))
        self.peak_label.config(text=f"Peak: {self._format_speed(self.peak_dl)} / {self._format_speed(self.peak_ul)}")

        # Blink connection indicator on activity
        if dl > 1 or ul > 1:
            self.connection_label.config(fg=FG_GREEN, text="\u25cf Active")
        elif dl > 0 or ul > 0:
            self.connection_label.config(fg=FG_YELLOW, text="\u25cf Idle")
        else:
            self.connection_label.config(fg=FG_RED, text="\u25cf Inactive")

        # Schedule next update
        self.root.after(1000, self._update_loop)

    def stop(self) -> None:
        """Stop monitoring and close the widget."""
        self.monitoring = False
        try:
            self.root.quit()
        except Exception:
            pass

    def run(self) -> None:
        """Run the tkinter main loop."""
        self.root.mainloop()


def launch_widget() -> None:
    """Launch the desktop speed widget.

    This is the main entry point for the widget mode.
    """
    if not HAS_TK:
        print("ERROR: tkinter is required for the desktop widget.")
        print("On Linux: sudo apt install python3-tk")
        print("On macOS: tkinter is included with Python")
        print("On Windows: tkinter is included with Python")
        sys.exit(1)

    print("SpeedMeter Widget — Live network speed monitor")
    print("Press ESC to close the widget window.\n")

    root = tk.Tk()
    widget = SpeedWidget(root)
    try:
        widget.run()
    except KeyboardInterrupt:
        widget.stop()
    except Exception as e:
        print(f"Widget error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    launch_widget()
