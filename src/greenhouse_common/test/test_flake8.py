"""Run flake8 over the package sources when ament_flake8 is available."""

import pytest

pytest.importorskip('ament_flake8')

from ament_flake8.main import main_with_errors  # noqa: E402


@pytest.mark.flake8
@pytest.mark.linter
def test_flake8():
    rc, errors = main_with_errors(argv=[])
    assert rc == 0, \
        'Found %d code style errors / warnings:\n' % len(errors) + \
        '\n'.join(errors)
