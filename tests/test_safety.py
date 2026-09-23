import pytest

from desk_radar.config import Settings
from desk_radar.safety import SafetyError, assert_locks


def test_locks_pass_by_default():
    assert_locks(Settings())


def test_live_flag_refuses_start():
    with pytest.raises(SafetyError):
        assert_locks(Settings(allow_live_trading=True, paper_trading=True, dry_run=True))


def test_paper_off_refuses_start():
    with pytest.raises(SafetyError):
        assert_locks(Settings(paper_trading=False, dry_run=True, allow_live_trading=False))
