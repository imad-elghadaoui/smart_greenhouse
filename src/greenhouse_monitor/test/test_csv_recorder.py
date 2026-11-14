# Copyright 2026 Imad Elghadaoui
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for greenhouse_monitor.csv_recorder."""

import csv

import pytest

from greenhouse_monitor.csv_recorder import CsvRecorder


def test_writes_header_and_rows(tmp_path):
    path = tmp_path / 'nested' / 'log.csv'
    recorder = CsvRecorder(str(path))
    recorder.open()
    recorder.append(1.5, 'temperature', 21.25)
    recorder.append(2.5, 'humidity', 58.0)
    recorder.close()

    with path.open(newline='') as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ['timestamp', 'topic', 'value']
    assert rows[1] == ['1.500000', 'temperature', '21.250000']
    assert rows[2] == ['2.500000', 'humidity', '58.000000']


def test_appends_to_existing_file_without_duplicating_header(tmp_path):
    path = tmp_path / 'log.csv'
    first = CsvRecorder(str(path))
    first.open()
    first.append(1.0, 'temperature', 20.0)
    first.close()

    second = CsvRecorder(str(path))
    second.open()
    second.append(2.0, 'temperature', 21.0)
    second.close()

    with path.open(newline='') as handle:
        rows = list(csv.reader(handle))
    assert sum(row[0] == 'timestamp' for row in rows) == 1
    assert len(rows) == 3


def test_append_without_open_raises(tmp_path):
    recorder = CsvRecorder(str(tmp_path / 'log.csv'))
    with pytest.raises(RuntimeError):
        recorder.append(0.0, 'temperature', 20.0)
