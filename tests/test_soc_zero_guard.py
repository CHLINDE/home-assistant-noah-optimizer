"""Regression tests for a sleeping NOAH reporting a false 0 % SOC."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from custom_components.noah_optimizer.soc_guard import SocZeroGuard


START = datetime(2026, 11, 7, 8, 0, tzinfo=timezone.utc)


def sample(guard, value, seconds=0, updated_seconds=None, minimum=10):
    return guard.observe(
        value,
        now=START + timedelta(seconds=seconds),
        source_updated_at=(
            START + timedelta(seconds=updated_seconds)
            if updated_seconds is not None
            else None
        ),
        minimum_soc=minimum,
    )


def test_cached_zero_during_reconnect_is_missing_not_zero():
    guard = SocZeroGuard()
    assert sample(guard, 10) == 10
    guard.reset_pending()  # NOAH goes offline overnight
    assert sample(guard, 0, 10, 0) is None
    assert sample(guard, 0, 80, 0) is None
    assert guard.last_trusted_soc == 10
    assert sample(guard, 11, 90, 90) == 11


def test_genuine_zero_requires_two_new_state_updates():
    guard = SocZeroGuard()
    assert sample(guard, 10) == 10
    assert sample(guard, 0, 10, 0) is None
    assert sample(guard, 0, 30, 20) is None
    assert sample(guard, 0, 50, 40) == 0
    assert guard.last_trusted_soc == 0
    assert sample(guard, 0, 60, 40) == 0


def test_zero_without_fresh_update_stays_untrusted():
    guard = SocZeroGuard()
    assert sample(guard, 0, 10, 0) is None
    assert sample(guard, 0, 900, 0) is None
    assert guard.last_trusted_soc is None


def test_zero_is_valid_when_configured_minimum_is_zero():
    guard = SocZeroGuard()
    assert sample(guard, 0, 10, minimum=0) == 0


def test_new_offline_episode_requires_revalidation():
    guard = SocZeroGuard()
    assert sample(guard, 0, 10) is None
    assert sample(guard, 0, 20, 20) is None
    assert sample(guard, 0, 50, 45) == 0
    guard.reset_pending()
    assert sample(guard, 0, 60, 45) is None


def test_non_numeric_or_missing_soc_is_not_trusted():
    guard = SocZeroGuard()
    assert sample(guard, 12, 0) == 12
    assert sample(guard, None, 5) is None
    assert guard.last_trusted_soc == 12
