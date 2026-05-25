<div align="center">
  <br/>
  <h1>🚀 SpeedMeter</h1>
  <h3>Terminal-Based Interactive Internet Speed Meter</h3>
  <p>
    <strong>Real-time bandwidth monitoring in your terminal.</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat&logo=python&logoColor=white" alt="Python 3.10+"/>
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="MIT License"/>
    <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey?style=flat" alt="Cross-platform"/>
    <img src="https://img.shields.io/badge/CLI-ready-brightgreen?style=flat" alt="CLI Ready"/>
    <img src="https://img.shields.io/badge/TUI-Textual-ff6b6b?style=flat" alt="Textual TUI"/>
  </p>
  <br/>
</div>

SpeedMeter is a **fully interactive, real-time internet speed meter** that runs entirely in your terminal. It combines a beautiful Textual-based Terminal UI (TUI) with the power of `speedtest-cli` to give you live download/upload speed tests, historical tracking, system resource monitoring, and interactive controls — all without leaving your command line.

---

## ✨ Features

- **Interactive Terminal UI** — Beautiful real-time dashboard with speed gauges, charts, and live data
- **Full Speed Tests** — Download speed, upload speed, ping, and jitter measurements
- **Live Speed Gauges** — Animated visual indicators for download, upload, and ping
- **Speed History Chart** — Sparkline-style chart showing test results over time
- **Server Browser** — Browse and select from available speedtest.net servers
- **System Monitor** — Live CPU, memory, uptime, and network traffic display
- **Test History** — Persistent storage of all speed test results (JSON-backed)
- **Quick Mode** — Run a one-shot speed test from the CLI without the TUI
- **Export Results** — Save test data to JSON files for analysis
- **Cross-Platform** — Works on Linux, macOS, and Windows
- **Configurable** — Custom themes, thresholds, units, and auto-refresh intervals

---

## 📸 Screenshots

```
 ┌─────────────────────────────────────────────────────────┐
 │  ╔═══════════════════════════════════════════════════╗  │
 │  ║  ┌─ Download ─┐  ┌─ Upload ───┐  ┌─ Ping ────┐  ║  │
 │  ║  │ 256.42 Mbps│  │  42.18 Mbps│  │ 12.3 ms   │  ║  │
 │  ║  │ ████████░░│  │  ████░░░░░░│  │ ░░░░░░░░░░│  ║  │
 │  ║  └────────────┘  └────────────┘  └────────────┘  ║  │
 │  ║  ┌─ Speed History ──────────────────────────────┐  ║  │
 │  ║  │ ▄▄▄▄▄▄▄███▀▀▀████▄▄▄▄▄▄███▀▀▀████████     │  ║  │
 │  ║  └──────────────────────────────────────────────┘  ║  │
 │  ║  ┌─ Connection ───┐  ┌─ System ───────────────┐  ║  │
 │  ║  │ Server: XYZ    │  │ CPU: 23.4%             │  ║  │
 │  ║  │ ISP: ABC       │  │ Memory: 45.2%          │  ║  │
 │  ║  │ IP: 1.2.3.4    │  │ Uptime: 12h 34m       │  ║  │
 │  ║  └────────────────┘  └────────────────────────┘  ║  │
 │  ║  [Run Test] [Stop] [History] [Quick Mode]        ║  │
 │  ║  ✓ 14:32:15 — DL: 256.42 | UL: 42.18 | 12.3ms   ║  │
 │  ╚═══════════════════════════════════════════════════╝  │
 └─────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **git** (optional, for cloning the repository)

### Option 1: Quick Install (Recommended)

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/fameux/speedmeter/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/fameux/speedmeter/main/install.ps1 | iex
```

### Option 2: Manual Install from Source

```bash
# Clone the repository
git clone https://github.com/fameux/speedmeter.git
cd speedmeter

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install SpeedMeter
pip install -e .
```

### Option 3: Install via pip (when published to PyPI)

```bash
pip install speedmeter
```

---

## 🚀 Usage

### Launch the Interactive TUI

```bash
speedmeter
```

This opens the full interactive terminal dashboard. Use keyboard shortcuts:

| Key | Action |
|-----|--------|
| `Space` / `R` | Run a speed test |
| `S` | View test history |
| `C` | View configuration |
| `D` | Toggle detail view |
| `Q` | Quit |
| `Tab` | Navigate between widgets |

### Quick Test (CLI Mode)

Run a single speed test and exit (no TUI):

```bash
speedmeter --quick
```

### List Available Servers

```bash
speedmeter --list-servers
```

### Test with a Specific Server

```bash
speedmeter --quick --server 12345
```

### Save Results to File

```bash
speedmeter --quick --output results.json
```

### Use a Custom Config

```bash
speedmeter --config /path/to/config.json
```

### Verbose Logging

```bash
speedmeter --verbose
```

### Check Version

```bash
speedmeter --version
```

### Run from Project Directory

```bash
python -m speedmeter
python -m speedmeter --quick
```

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
    "refresh_interval": 5,
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
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_speedmeter.py

# Run without network-dependent tests
pytest -m "not network"
```

---

## 🏗️ Project Structure

```
speedmeter/
├── speedmeter/              # Main package
│   ├── __init__.py          # Package init
│   ├── __main__.py          # CLI entry point & arg parsing
│   ├── app.py               # Textual TUI application
│   ├── config.py            # Configuration management
│   ├── history.py           # Test history persistence
│   ├── tester.py            # Speed test execution
│   └── widgets.py           # Custom Textual widgets
├── tests/
│   └── test_speedmeter.py   # Pytest test suite
├── install.sh               # Unix installation script
├── install.ps1              # Windows installation script
├── uninstall.sh             # Unix uninstallation script
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
| `rich` | Terminal rendering with styled output and progress bars |
| `textual` | Terminal UI framework for interactive layouts |
| `prompt_toolkit` | Interactive terminal input and key bindings |
| `psutil` | System resource monitoring (CPU, memory, network) |
| `colorama` | Cross-platform terminal color support (Windows) |
| `platformdirs` | Standard OS paths for config, cache, and logs |
| `requests` | HTTP fallback and API-based network checks |
| `asyncio` | Non-blocking async operations for live UI |
| `argparse` | CLI argument parsing |
| `logging` | Runtime event and error logging |
| `pytest` | Automated test suite |

---

## 🖥️ Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✅ Full support | Tested on Ubuntu 22.04+, Fedora |
| macOS | ✅ Full support | Tested on macOS 13+ (Apple Silicon & Intel) |
| Windows | ✅ Full support | Tested on Windows 10/11 (PowerShell, cmd, Git Bash) |

### Terminal Requirements

- **256-color support** recommended (most modern terminals)
- Minimum **80×24** terminal size
- Works in: GNOME Terminal, iTerm2, Windows Terminal, Alacritty, Kitty, tmux, VS Code integrated terminal

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/fameux/speedmeter.git
cd speedmeter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [speedtest-cli](https://github.com/sivel/speedtest-cli) — Internet speed test library
- [Textual](https://github.com/Textualize/textual) — Terminal UI framework
- [Rich](https://github.com/Textualize/rich) — Terminal formatting library

---

<div align="center">
  <p>
    <sub>Made with ❤️ for the terminal community</sub>
    <br/>
    <sub>SpeedMeter v1.0.0</sub>
  </p>
</div>