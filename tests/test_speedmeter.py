"""Tests for SpeedMeter modules."""
import json
import os
import sys
import tempfile
import time

import pytest

from speedmeter.config import get_default_config, load_config, save_config
from speedmeter.history import HistoryManager
from speedmeter.tester import SpeedTestResult, SpeedTester


# =============================================================================
# Config Tests
# =============================================================================

class TestConfig:
    """Test configuration module."""

    def test_default_config_has_required_keys(self):
        """Default config should have all required sections."""
        config = get_default_config()
        assert "app" in config
        assert "paths" in config
        assert "units" in config
        assert "notifications" in config
        assert config["app"]["refresh_interval"] == 5
        assert config["app"]["history_size"] == 50

    def test_load_config_nonexistent(self):
        """Loading a nonexistent config should return defaults."""
        config = load_config("/nonexistent/path/config.json")
        assert config["app"]["refresh_interval"] == 5

    def test_save_and_load_config(self):
        """Config should persist to disk correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = get_default_config()
            config["app"]["refresh_interval"] = 10
            config["units"]["speed"] = "MB/s"

            assert save_config(config, path) is True

            loaded = load_config(path)
            assert loaded["app"]["refresh_interval"] == 10
            assert loaded["units"]["speed"] == "MB/s"
        finally:
            os.unlink(path)


# =============================================================================
# SpeedTestResult Tests
# =============================================================================

class TestSpeedTestResult:
    """Test SpeedTestResult dataclass."""

    def test_create_valid_result(self):
        """Creating a valid result should work."""
        result = SpeedTestResult(
            timestamp=time.time(),
            download_bps=100_000_000,
            upload_bps=50_000_000,
            ping_ms=15.0,
            download_mbps=100.0,
            upload_mbps=50.0,
            server_name="Test Server",
            server_location="Test Location",
        )
        assert result.is_valid is True
        assert result.download_mbps == 100.0
        assert result.upload_mbps == 50.0
        assert result.ping_ms == 15.0

    def test_result_with_error(self):
        """A result with an error should not be valid."""
        result = SpeedTestResult(error="Network error")
        assert result.is_valid is False

    def test_result_zero_speed(self):
        """A result with zero speed should not be valid."""
        result = SpeedTestResult(download_mbps=0, upload_mbps=0)
        assert result.is_valid is False

    def test_result_to_dict(self):
        """Result should serialize to dict correctly."""
        result = SpeedTestResult(
            timestamp=1000.0,
            download_mbps=100.0,
            upload_mbps=50.0,
            ping_ms=15.0,
            server_name="Srv",
        )
        d = result.to_dict()
        assert d["download_mbps"] == 100.0
        assert d["upload_mbps"] == 50.0
        assert d["ping_ms"] == 15.0
        assert d["server_name"] == "Srv"

    def test_result_from_dict(self):
        """Result should deserialize from dict correctly."""
        data = {
            "timestamp": 1000.0,
            "download_mbps": 100.0,
            "upload_mbps": 50.0,
            "ping_ms": 15.0,
            "server_name": "Srv",
        }
        result = SpeedTestResult.from_dict(data)
        assert result.download_mbps == 100.0
        assert result.upload_mbps == 50.0
        assert result.server_name == "Srv"

    def test_result_to_json(self):
        """Result should serialize to valid JSON."""
        result = SpeedTestResult(
            timestamp=1000.0,
            download_mbps=100.0,
            upload_mbps=50.0,
            ping_ms=15.0,
        )
        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert parsed["download_mbps"] == 100.0

    def test_result_format_string(self):
        """Format should produce a readable string."""
        result = SpeedTestResult(
            timestamp=time.time(),
            download_mbps=100.0,
            upload_mbps=50.0,
            ping_ms=15.0,
            server_name="Test",
            server_location="Loc",
        )
        formatted = result.format()
        assert "Download" in formatted
        assert "100.00" in formatted
        assert "50.00" in formatted
        assert "15.0" in formatted

    def test_result_format_error(self):
        """Format with error should show error message."""
        result = SpeedTestResult(error="Connection timeout")
        formatted = result.format()
        assert "Connection timeout" in formatted


# =============================================================================
# HistoryManager Tests
# =============================================================================

class TestHistoryManager:
    """Test history management."""

    def test_empty_history(self):
        """Fresh history should be empty."""
        hm = HistoryManager(max_size=10)
        assert hm.get_count() == 0
        assert hm.get_all() == []
        assert hm.get_latest() is None

    def test_add_result(self):
        """Adding results should work."""
        hm = HistoryManager(max_size=10)
        r1 = SpeedTestResult(download_mbps=100, upload_mbps=50, ping_ms=10)
        r2 = SpeedTestResult(download_mbps=200, upload_mbps=80, ping_ms=5)
        hm.add(r1)
        hm.add(r2)
        assert hm.get_count() == 2

    def test_history_ordering(self):
        """Results should be newest first."""
        hm = HistoryManager(max_size=10)
        r1 = SpeedTestResult(timestamp=100, download_mbps=100, upload_mbps=50, ping_ms=10)
        r2 = SpeedTestResult(timestamp=200, download_mbps=200, upload_mbps=80, ping_ms=5)
        hm.add(r1)
        hm.add(r2)
        all_results = hm.get_all()
        assert all_results[0].timestamp == 200

    def test_history_max_size(self):
        """History should respect max_size."""
        hm = HistoryManager(max_size=3)
        for i in range(5):
            hm.add(SpeedTestResult(
                timestamp=float(i),
                download_mbps=float(100 + i),
                upload_mbps=float(50 + i),
                ping_ms=10.0,
            ))
        assert hm.get_count() == 3

    def test_clear_history(self):
        """Clearing history should remove all entries."""
        hm = HistoryManager(max_size=10)
        hm.add(SpeedTestResult(download_mbps=100, upload_mbps=50, ping_ms=10))
        hm.add(SpeedTestResult(download_mbps=200, upload_mbps=80, ping_ms=5))
        hm.clear()
        assert hm.get_count() == 0

    def test_average_download(self):
        """Average download calculation should work."""
        hm = HistoryManager(max_size=10)
        for i in range(1, 6):
            hm.add(SpeedTestResult(
                download_mbps=float(i * 50),
                upload_mbps=25.0,
                ping_ms=10.0,
            ))
        avg = hm.get_average_download(5)
        assert avg == 150.0  # (50+100+150+200+250)/5

    def test_max_min_download(self):
        """Max and min calculations should work."""
        hm = HistoryManager(max_size=10)
        hm.add(SpeedTestResult(download_mbps=100, upload_mbps=50, ping_ms=10))
        hm.add(SpeedTestResult(download_mbps=500, upload_mbps=80, ping_ms=5))
        hm.add(SpeedTestResult(download_mbps=50, upload_mbps=30, ping_ms=20))
        assert hm.get_max_download() == 500.0
        assert hm.get_min_download() == 50.0

    def test_invalid_results_not_stored(self):
        """Invalid results should not be stored."""
        hm = HistoryManager(max_size=10)
        hm.add(SpeedTestResult(error="Failed"))
        assert hm.get_count() == 0

    def test_add_zero_speed_not_stored(self):
        """Zero speed results should not be stored."""
        hm = HistoryManager(max_size=10)
        hm.add(SpeedTestResult(download_mbps=0, upload_mbps=0, ping_ms=0))
        assert hm.get_count() == 0

    def test_persistence(self):
        """History should persist to disk and load back."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            hm = HistoryManager(max_size=10, file_path=path)
            hm.add(SpeedTestResult(
                timestamp=1000,
                download_mbps=100,
                upload_mbps=50,
                ping_ms=10,
                server_name="Test",
            ))

            # Create a new instance with same file
            hm2 = HistoryManager(max_size=10, file_path=path)
            assert hm2.get_count() == 1
            assert hm2.get_latest().download_mbps == 100
        finally:
            os.unlink(path)

    def test_export_json(self):
        """Exporting history to JSON should work."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            hm = HistoryManager(max_size=10)
            hm.add(SpeedTestResult(
                timestamp=1000,
                download_mbps=100,
                upload_mbps=50,
                ping_ms=10,
            ))
            success = hm.export_json(path)
            assert success is True
            with open(path) as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]["download_mbps"] == 100
        finally:
            os.unlink(path)

    def test_get_last(self):
        """Getting last N results should work."""
        hm = HistoryManager(max_size=10)
        for i in range(1, 6):
            hm.add(SpeedTestResult(
                timestamp=float(i),
                download_mbps=float(i * 100),
                upload_mbps=50.0,
                ping_ms=10.0,
            ))
        last = hm.get_last(2)
        assert len(last) == 2
        assert last[-1].timestamp == 4  # oldest of the last 2
        assert last[0].timestamp == 5  # newest of the last 2


# =============================================================================
# SpeedTester Tests
# =============================================================================

class TestSpeedTester:
    """Test SpeedTester (without actual network calls)."""

    def test_tester_init(self):
        """Tester should initialize with defaults."""
        tester = SpeedTester(server_id=12345, timeout=15)
        assert tester.server_id == 12345
        assert tester.timeout == 15

    def test_tester_default_server(self):
        """Tester should default to auto server selection."""
        tester = SpeedTester()
        assert tester.server_id is None
        assert tester.timeout == 30


# =============================================================================
# Integration: Command-Line Parsing
# =============================================================================

class TestCLI:
    """Test command-line argument parsing."""

    def test_cli_quick(self):
        """--quick flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["--quick"])
        assert args.quick is True

    def test_cli_server(self):
        """-s/--server flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["--server", "12345"])
        assert args.server == 12345

    def test_cli_output(self):
        """-o/--output flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["--output", "results.json"])
        assert args.output == "results.json"

    def test_cli_version(self):
        """--version flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["--version"])
        assert args.version is True

    def test_cli_list_servers(self):
        """--list-servers flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["--list-servers"])
        assert args.list_servers is True

    def test_cli_verbose(self):
        """-v/--verbose flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["-v"])
        assert args.verbose is True

    def test_cli_config(self):
        """-c/--config flag should be parsed."""
        from speedmeter.__main__ import parse_args
        args = parse_args(["--config", "/path/to/config.json"])
        assert args.config == "/path/to/config.json"


if __name__ == "__main__":
    pytest.main(["-v", __file__])