"""Test history management — stores, loads, and queries past speed test results."""

import json
import logging
import os
import threading
from collections import deque
from typing import Any, Dict, List, Optional

from speedmeter.tester import SpeedTestResult

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages a rolling history of speed test results with file persistence."""

    def __init__(self, max_size: int = 50, file_path: Optional[str] = None):
        self.max_size = max_size
        self.file_path = file_path
        self._lock = threading.Lock()
        self._results: deque[SpeedTestResult] = deque(maxlen=max_size)
        self._load_from_disk()

    def add(self, result: SpeedTestResult) -> None:
        """Add a result to history and persist."""
        if not result or not result.is_valid:
            return
        with self._lock:
            self._results.append(result)
        self._save_to_disk()

    def get_all(self) -> List[SpeedTestResult]:
        """Get all stored results, newest first."""
        with self._lock:
            return list(reversed(self._results))

    def get_last(self, n: int = 1) -> List[SpeedTestResult]:
        """Get the last N results."""
        if n <= 0:
            return []
        with self._lock:
            items = list(self._results)
            return items[-n:]

    def get_latest(self) -> Optional[SpeedTestResult]:
        """Get the most recent result."""
        results = self.get_last(1)
        return results[0] if results else None

    def clear(self) -> None:
        """Clear all history."""
        with self._lock:
            self._results.clear()
        self._save_to_disk()

    def get_average_download(self, n: int = 5) -> float:
        """Get average download speed over last N tests."""
        results = self.get_last(n)
        valid = [r.download_mbps for r in results if r.is_valid]
        return sum(valid) / len(valid) if valid else 0.0

    def get_average_upload(self, n: int = 5) -> float:
        """Get average upload speed over last N tests."""
        results = self.get_last(n)
        valid = [r.upload_mbps for r in results if r.is_valid]
        return sum(valid) / len(valid) if valid else 0.0

    def get_max_download(self) -> float:
        """Get the maximum download speed recorded."""
        with self._lock:
            valid = [r.download_mbps for r in self._results if r.is_valid]
        return max(valid) if valid else 0.0

    def get_min_download(self) -> float:
        """Get the minimum download speed recorded."""
        with self._lock:
            valid = [r.download_mbps for r in self._results if r.is_valid]
        return min(valid) if valid else 0.0

    def get_count(self) -> int:
        """Get total number of results stored."""
        with self._lock:
            return len(self._results)

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Export all results as list of dicts."""
        with self._lock:
            return [r.to_dict() for r in self._results]

    def export_json(self, path: str) -> bool:
        """Export all history to a JSON file."""
        try:
            with open(path, "w") as f:
                json.dump(self.to_dicts(), f, indent=2, default=str)
            return True
        except IOError as e:
            logger.error("Failed to export history: %s", e)
            return False

    def _load_from_disk(self) -> None:
        """Load history from disk on initialization."""
        if not self.file_path or not os.path.isfile(self.file_path):
            return
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    result = SpeedTestResult.from_dict(item)
                    if result.is_valid:
                        self._results.append(result)
            logger.info("Loaded %d history entries from %s", len(self._results), self.file_path)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Could not load history from %s: %s", self.file_path, e)

    def _save_to_disk(self) -> None:
        """Persist history to disk."""
        if not self.file_path:
            return
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with self._lock:
                data = [r.to_dict() for r in self._results]
                with open(self.file_path, "w") as f:
                    json.dump(data, f, indent=2, default=str)
        except IOError as e:
            logger.error("Failed to save history: %s", e)
