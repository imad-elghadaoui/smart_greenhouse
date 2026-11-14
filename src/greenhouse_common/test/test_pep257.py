"""Run pydocstyle over the package sources when ament_pep257 is available."""

import pytest

pytest.importorskip('ament_pep257')

from ament_pep257.main import main  # noqa: E402


@pytest.mark.linter
@pytest.mark.pep257
def test_pep257():
    rc = main(argv=['.', 'test'])
    assert rc == 0, 'Found code style errors / warnings'
