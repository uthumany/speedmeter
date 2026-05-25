"""Speed test execution and result handling."""
import json
import logging
import time
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

try:
    import speedtest
    HAS_SPEEDTEST = True
except ImportError:
    HAS_SPEEDTEST = False

logger = logging.getLogger(__name__)


@dataclass
class SpeedTestResult:
    """Represents a single speed test result."""
    timestamp: float = 0.0
    download_bps: float = 0.0
    upload_bps: float = 0.0
    ping_ms: float = 0.0
    jitter_ms: float = 0.0
    download_mbps: float = 0.0
    upload_mbps: float = 0.0
    server_name: str = ""
    server_location: str = ""
    server_country: str = ""
    server_host: str = ""
    server_id: int = 0
    bytes_downloaded: int = 0
    bytes_uploaded: int = 0
    isp: str = ""
    external_ip: str = ""
    error: Optional[str] = None
    duration_seconds: float = 0.0

    def format(self, precision: int = 2) -> str:
        """Format result as a human-readable string."""
        if self.error:
            return f"Error: {self.error}"
        lines = [
            f"Download:   {self.download_mbps:.{precision}f} Mbps",
            f"Upload:     {self.upload_mbps:.{precision}f} Mbps",
            f"Ping:       {self.ping_ms:.1f} ms",
        ]
        if self.jitter_ms > 0:
            lines.append(f"Jitter:     {self.jitter_ms:.1f} ms")
        lines.append(f"Server:     {self.server_name} ({self.server_location})")
        if self.isp:
            lines.append(f"ISP:        {self.isp}")
        if self.external_ip:
            lines.append(f"IP:         {self.external_ip}")
        lines.append(f"Timestamp:  {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpeedTestResult":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @property
    def is_valid(self) -> bool:
        """Check if result has valid data."""
        return not self.error and self.download_mbps > 0


class SpeedTester:
    """Handles internet speed test execution with progress tracking."""

    def __init__(
        self,
        server_id: Optional[int] = None,
        timeout: int = 30,
        callback: Optional[callable] = None,
    ):
        self.server_id = server_id
        self.timeout = timeout
        self.callback = callback  # callback(stage: str, progress: float)
        self._start_time = 0.0

    def _make_callback(self, action: str):
        """Create a closure that reports progress for a specific action.

        Speedtest-cli calls the callback as ``callback(current, total)``
        without passing the action name, so we bind the action here.
        """
        if not self.callback:
            return None

        stage_map = {
            "download": "Downloading",
            "upload": "Uploading",
            "ping": "Testing Ping",
            "waiting": "Waiting",
            "init": "Initializing",
            "finding_server": "Finding Server",
        }
        stage = stage_map.get(action, action.capitalize())

        def cb(current: float, total: float, **kwargs) -> None:
            progress = current / total if total > 0 else 0
            self.callback(stage, progress)

        return cb

    def run_test(self) -> SpeedTestResult:
        """Execute a full speed test and return the result."""
        self._start_time = time.time()
        result = SpeedTestResult(timestamp=self._start_time)

        if not HAS_SPEEDTEST:
            result.error = "speedtest-cli is not installed. Install with: pip install speedtest-cli"
            return result

        try:
            if self.callback:
                self.callback("Finding Server", 0.0)

            st = speedtest.Speedtest(secure=True)

            # Find best server or use specified one
            if self.server_id:
                st.get_servers([self.server_id])
            else:
                st.get_best_server()

            server = st.results.server or {}
            result.server_name = server.get("name", "")
            result.server_location = server.get("sponsor", server.get("name", ""))
            result.server_country = server.get("country", "")
            result.server_host = server.get("host", "")
            result.server_id = int(server.get("id", 0))
            result.isp = st.results.client.get("isp", "") if hasattr(st.results, 'client') else ""
            result.external_ip = st.results.client.get("ip", "") if hasattr(st.results, 'client') else ""

            # Ping test
            if self.callback:
                self.callback("Testing Ping", 0.0)
            st.results.ping = server.get("lat", 0)
            result.ping_ms = float(st.results.ping)

            # Download test
            if self.callback:
                self.callback("Downloading", 0.0)

            st.download(callback=self._make_callback("download"))
            result.download_bps = st.results.download
            result.download_mbps = st.results.download / 1_000_000
            result.bytes_downloaded = st.results.bytes_received if hasattr(st.results, 'bytes_received') else 0

            # Upload test
            if self.callback:
                self.callback("Uploading", 0.0)

            st.upload(callback=self._make_callback("upload"))
            result.upload_bps = st.results.upload
            result.upload_mbps = st.results.upload / 1_000_000
            result.bytes_uploaded = st.results.bytes_sent if hasattr(st.results, 'bytes_sent') else 0

            # Jitter — speedtest-cli doesn't expose per-packet variance,
            # so jitter stays at the dataclass default of 0.0 by design.

            result.duration_seconds = time.time() - self._start_time
            result.timestamp = self._start_time

            logger.info(
                "Speed test complete: %.2f Mbps down / %.2f Mbps up / %.1f ms ping",
                result.download_mbps, result.upload_mbps, result.ping_ms,
            )

        except speedtest.SpeedtestException as e:
            result.error = str(e)
            logger.error("Speed test failed: %s", e)
        except Exception as e:
            result.error = str(e)
            logger.error("Unexpected error during speed test: %s", e, exc_info=True)

        return result

    def run_download_only(self) -> float:
        """Run only the download test and return Mbps."""
        if not HAS_SPEEDTEST:
            return 0.0
        try:
            st = speedtest.Speedtest(secure=True)
            if self.server_id:
                st.get_servers([self.server_id])
            else:
                st.get_best_server()
            st.download()
            return st.results.download / 1_000_000
        except Exception:
            return 0.0

    def run_upload_only(self) -> float:
        """Run only the upload test and return Mbps."""
        if not HAS_SPEEDTEST:
            return 0.0
        try:
            st = speedtest.Speedtest(secure=True)
            if self.server_id:
                st.get_servers([self.server_id])
            else:
                st.get_best_server()
            st.upload()
            return st.results.upload / 1_000_000
        except Exception:
            return 0.0

    def run_ping_only(self) -> float:
        """Run only the ping test and return ms."""
        if not HAS_SPEEDTEST:
            return 0.0
        try:
            st = speedtest.Speedtest(secure=True)
            if self.server_id:
                st.get_servers([self.server_id])
            else:
                st.get_best_server()
            return float(st.results.ping)
        except Exception:
            return 0.0


def run_quick_test(
    server_id: Optional[int] = None,
    output: Optional[str] = None,
) -> Optional[SpeedTestResult]:
    """Run a one-shot speed test and optionally save results."""
    print("Running speed test...")
    tester = SpeedTester(server_id=server_id)

    def progress(stage, pct):
        bar_len = 30
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r  {stage}: [{bar}] {pct*100:.0f}%", end="", flush=True)

    tester.callback = progress
    result = tester.run_test()
    print()

    if result.error:
        print(f"  ERROR: {result.error}")
        return result

    print(f"\n{result.format()}")
    print(f"  Duration: {result.duration_seconds:.1f}s")

    if output:
        try:
            with open(output, "w") as f:
                f.write(result.to_json())
            print(f"  Results saved to: {output}")
        except IOError as e:
            print(f"  WARNING: Could not save results: {e}")

    return result


def list_servers() -> List[Dict[str, Any]]:
    """List available speedtest.net servers."""
    if not HAS_SPEEDTEST:
        return []
    try:
        st = speedtest.Speedtest(secure=True)
        servers = st.get_servers()
        result = []
        for server_list in servers.values():
            for s in server_list:
                result.append({
                    "id": s.get("id", 0),
                    "name": s.get("name", ""),
                    "location": s.get("sponsor", s.get("name", "")),
                    "country": s.get("country", ""),
                    "sponsor": s.get("sponsor", ""),
                    "host": s.get("host", ""),
                })
        return sorted(result, key=lambda x: x["id"])
    except Exception as e:
        logger.error("Failed to list servers: %s", e)
        return []