"""Append-only CSV recorder used by the data logger node."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional, TextIO, Tuple


class CsvRecorder:
    """
    Write timestamped sensor samples to a CSV file.

    The file is opened in append mode and flushed after every row so that a
    crash does not lose buffered samples. The header is only written when the
    file is created, so restarts append to the existing log.
    """

    def __init__(
        self,
        path: str,
        header: Tuple[str, ...] = ('timestamp', 'topic', 'value'),
    ) -> None:
        self._path = Path(path)
        self._header = header
        self._file: Optional[TextIO] = None
        self._writer: Optional[csv.writer] = None

    @property
    def path(self) -> Path:
        """Return the destination file path."""
        return self._path

    def open(self) -> None:
        """Create the parent directory and open the file for appending."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        is_empty = not self._path.exists() or self._path.stat().st_size == 0
        self._file = self._path.open('a', newline='', encoding='utf-8')
        self._writer = csv.writer(self._file)
        if is_empty:
            self._writer.writerow(self._header)
            self._file.flush()

    def append(self, timestamp: float, topic: str, value: float) -> None:
        """Append one sample to the file."""
        if self._writer is None or self._file is None:
            raise RuntimeError('recorder is not open')
        self._writer.writerow([f'{timestamp:.6f}', topic, f'{value:.6f}'])
        self._file.flush()

    def close(self) -> None:
        """Flush and close the file if it is open."""
        if self._file is not None:
            self._file.close()
        self._file = None
        self._writer = None
