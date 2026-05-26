<div align="center">
  <br/>
  <h1>🚀 SpeedMeter</h1>
  <h3>Cyberpunk Terminal Internet Speed Meter</h3>
  <p>
    <strong>Real-time bandwidth monitoring with a neon HUD interface.</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat&logo=python&logoColor=white" alt="Python 3.10+"/>
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="MIT License"/>
    <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey?style=flat" alt="Cross-platform"/>
    <img src="https://img.shields.io/badge/CLI-ready-brightgreen?style=flat" alt="CLI Ready"/>
    <img src="https://img.shields.io/badge/TUI-Textual-ff6b6b?style=flat" alt="Textual TUI"/>
    <img src="https://github.com/uthumany/speedmeter/actions/workflows/ci.yml/badge.svg" alt="CI Status"/>
  </p>
  <br/>
</div>

SpeedMeter is a **cyberpunk-styled, real-time internet speed meter** that runs in your terminal. It features a neon HUD interface, continuous live network traffic monitoring, full Ookla speed tests, and an optional desktop widget — all free and local-only.

---

## ✨ Features

- **Continuous Live Monitoring** — Real-time download/upload traffic tracking via `psutil`
- **Cyberpunk HUD Interface** — Neon green, cyan, magenta gauges with animated bars
- **Full Speed Tests** — Download, upload, ping, and jitter via speedtest.net
- **Live Monitor Display** — Peak, average, and current traffic with sparkline visualization
- **Speed History Chart** — Sparkline chart showing test results over time
- **Desktop GUI Widget** — Small always-on-top window mirroring live network speeds
- **Server Browser** — Browse and select from available speedtest.net servers
- **System Monitor** — Live CPU, memory, uptime, and cumulative network traffic
- **Test History** — Persistent JSON-backed storage of all speed test results
- **Quick CLI Mode** — One-shot speed test without the TUI
- **Export Results** — Save test data to JSON files for analysis
- **Keyboard-First** — Full keyboard-driven interaction, zero mouse dependency
- **Cross-Platform** — Works on Linux, macOS, and Windows
- **Configurable** — Custom themes, thresholds, units, and auto-refresh intervals

---

## 🚀 Usage

### Launch the Interactive TUI

```bash
speedmeter
```

Opens the cyberpunk neon dashboard. Keyboard shortcuts:

| Key | Action |
|-----|--------|
| `Space` / `R` | Run a speed test |
| `M` | Toggle continuous network monitoring |
| `S` | View test history |
| `C` | View configuration |
| `D` | Toggle detail view |
| `Q` | Quit |

### Continuous Monitoring Mode

Start the TUI with live traffic monitoring enabled from launch:

```bash
speedmeter --monitor
```

Press `M` inside the TUI to start/stop monitoring at any time. The **Monitor Display** panel shows:
- Live download speed (Mbps)
- Live upload speed (Mbps)
- Peak speeds since monitoring started
- Average download/upload
- ASCII sparkline bars for visual traffic intensity

### Desktop GUI Widget

Launch a lightweight always-on-top widget window:

```bash
speedmeter --widget
```

The widget shows live download/upload speeds, peak values, and connection status. Press `Escape` to close.

### Quick Test (CLI Mode)

```bash
# Run a quick speed test and exit
speedmeter --quick

# Test with a specific server
speedmeter --quick --server 12345

# Save results to file
speedmeter --quick --output results.json
```

### List Available Servers

```bash
speedmeter --list-servers
```

### Other Commands

```bash
# Custom config
speedmeter --config /path/to/config.json

# Verbose logging
speedmeter --verbose

# Check version
speedmeter --version

# Run from project directory
python -m speedmeter
python -m speedmeter --quick
python -m speedmeter --monitor
python -m speedmeter --widget
```

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **git** (optional, for cloning)

### Quick Install (Recommended)

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/uthumany/speedmeter/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/uthumany/speedmeter/main/install.ps1 | iex
```

### Manual Install from Source

```bash
git clone https://github.com/uthumany/speedmeter.git
cd speedmeter
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Desktop Widget Requirements

The desktop widget requires **tkinter** (usually bundled with Python):
- **Linux**: `sudo apt install python3-tk`
- **macOS / Windows**: Included with Python by default

---

## 📸 Screenshots

```
 ┌──────────────────────────────────────────────────────────┐
 │  ╔══════════════════════════════════════════════════════╗  │
 │  ║  ┌─ DOWNLOAD ─┐  ┌─ UPLOAD ───┐  ┌─ PING ──────┐  ║  │
 │  ║  │ 256.42 Mbps│  │  42.18 Mbps│  │ 12.3 ms     │  ║  │
 │  ║  │ ████████░░│  │  ████░░░░░░│  │ ░░░░░░░░░░░░│  ║  │
 │  ║  └────────────┘  └────────────┘  └──────────────┘  ║  │
 │  ║  ┌─ LIVE MONITOR ──────────────────────────────────┐  ║  │
 │  ║  │ ↓ LIVE DL: 45.23 Mbps   PEAK: 256.42 Mbps      │  ║  │
 │  ║  │ ↑ LIVE UL: 12.89 Mbps   AVG: 128.1 / 22.4      │  ║  │
 │  ║  │ ↓ ████████░░░░░░░░░░░░░░░░░░░░░░               │  ║  │
 │  ║  │ ↑ ████░░░░░░░░░░░░░░░░░░░░░░░░░░               │  ║  │
 │  ║  └─────────────────────────────────────────────────┘  ║  │
 │  ║  ┌─ SPEED HISTORY ────────────────────────────────┐  ║  │
 │  ║  │ ▄▄▄▄▄▄▄███▀▀▀████▄▄▄▄▄▄███▀▀▀████████       │  ║  │
 │  ║  └────────────────────────────────────────────────┘  ║  │
 │  ║  ┌─ CONNECTION ─┐  ┌─ SYS ─────────────────────┐  ║  │
 │  ║  │ SRV: XYZ     │  │ CPU: 23.4%                │  ║  │
 │  ║  │ ISP: ABC     │  │ MEM: 45.2%                │  ║  │
 │  ║  │ IP: 1.2.3.4  │  │ UP: 12h 34m               │  ║  │
 │  ║  └──────────────┘  └────────────────────────────┘  ║  │
 │  ║  [RUN TEST] [MONITOR] [STOP] [HISTORY]             ║  │
 │  ║  ✓ 14:32:15 — DL: 256.42 | UL: 42.18 | 12.3ms     ║  │
 │  ╚══════════════════════════════════════════════════════╝  │
 └──────────────────────────────────────────────────────────┘
```

*Screenshots and GIFs coming soon. Run `speedmeter` to see the real thing.*

---

## 🎛️ Configuration

Configuration is stored at standard OS locations via `platformdirs`:

| OS | Config Path |
|----|-------------|
| Linux | `~/.config/speedmeter/config.json` |
| macOS | `~/Library/Application Support/speedmeter/config.json` |
| Windows | `C:\Users\<USER>\AppData\Local\speedmeter\config.json` |

### Default Configuration

```json
{
  "app": {
    "refresh_interval": 1,
    "theme": "auto",
    "history_size": 50,
    "chart_points": 30,
    "timeout": 30
  },
  "units": {
    "speed": "Mbps",
    "precision": 2
  },
  "notifications": {
    "enabled": true,
    "threshold_download": null,
    "threshold_upload": null
  }
}
```

---

## 🧪 Running Tests

```bash
make install-dev
make test
# or directly:
pip install -e ".[dev]"
pytest -v
```

---

## 🏗️ Project Structure

```
speedmeter/
├── speedmeter/              # Main package
│   ├── __init__.py          # Package init & version
│   ├── __main__.py          # CLI entry point & arg parsing
│   ├── app.py               # Textual TUI application (cyberpunk theme)
│   ├── config.py            # Configuration management
│   ├── history.py           # Test history persistence
│   ├── tester.py            # Speed test + NetworkMonitor class
│   ├── widgets.py           # Cyberpunk-styled Textual widgets
│   ├── widget_gui.py        # Desktop GUI widget (tkinter)
│   └── widget.spec          # PyInstaller spec
├── tests/
│   └── test_speedmeter.py   # 55+ pytest test suite
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI (3 OS × 3 Python versions)
├── install.sh               # Unix installation script
├── install.ps1              # Windows installation script
├── uninstall.sh             # Unix uninstallation script
├── Makefile                 # Build automation targets
├── ruff.toml                # Ruff linter configuration
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup script
├── pyproject.toml           # Modern build configuration
├── pytest.ini               # Pytest configuration
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── README.md                # This file
```

---

## 🧰 Dependencies

| Package | Purpose |
|---------|---------|
| `speedtest-cli` | Internet speed test engine (download, upload, ping) |
| `rich` | Terminal rendering with styled output |
| `textual` | Terminal UI framework for interactive layouts |
| `psutil` | System resource + real-time network traffic monitoring |
| `platformdirs` | Standard OS paths for config, cache, and logs |
| `tkinter` | Desktop GUI widget (usually bundled with Python) |

---

## 🖥️ Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✅ Full support | Tested on Ubuntu 22.04+, Fedora |
| macOS | ✅ Full support | Tested on macOS 13+ (Apple Silicon & Intel) |
| Windows | ✅ Full support | Tested on Windows 10/11 (PowerShell, cmd, Git Bash) |

### Terminal Requirements

- **256-color support** recommended (most modern terminals do)
- Minimum **80×24** terminal size
- Works in: GNOME Terminal, iTerm2, Windows Terminal, Alacritty, Kitty, tmux, VS Code

---

## 🛠️ Development

```bash
git clone https://github.com/uthumany/speedmeter.git
cd speedmeter
python3 -m venv venv
source venv/bin/activate
make install-dev

# Run tests
make test

# Lint & format
make lint
make format

# Build desktop widget executable
make build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## 🤝 Contributing

1. **Fork** the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- [speedtest-cli](https://github.com/sivel/speedtest-cli) — Internet speed test library
- [Textual](https://github.com/Textualize/textual) — Terminal UI framework
- [Rich](https://github.com/Textualize/rich) — Terminal formatting library
- [psutil](https://github.com/giampaolo/psutil) — System & network monitoring

---

<div align="center">
  <p>
    <sub>Made with ❤️ for the terminal community</sub>
    <br/>
    <sub>SpeedMeter v1.1.0 — Cyberpunk Edition</sub>
  </p>
</div>