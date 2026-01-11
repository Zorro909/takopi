"""Tests for Matrix availability checking."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from takopi.matrix.availability import (
    NioAvailability,
    check_basic_nio,
    check_e2ee_available,
    check_nio_availability,
)


def test_check_basic_nio_when_installed() -> None:
    """check_basic_nio returns True when nio is installed."""
    assert check_basic_nio() is True


def test_check_basic_nio_when_missing() -> None:
    """check_basic_nio returns False when nio import fails."""
    with patch("builtins.__import__", side_effect=ImportError("nio not found")):
        assert check_basic_nio() is False


def test_check_e2ee_available_strict_mode() -> None:
    """Strict mode validates Olm can be imported."""
    result = check_e2ee_available(strict=True)
    # Result depends on whether nio[e2e] is actually installed
    assert isinstance(result, bool)


def test_check_e2ee_available_lenient_mode() -> None:
    """Lenient mode only checks hasattr."""
    result = check_e2ee_available(strict=False)
    assert isinstance(result, bool)


def test_check_nio_availability_returns_dataclass() -> None:
    """check_nio_availability returns NioAvailability dataclass."""
    result = check_nio_availability()
    assert isinstance(result, NioAvailability)
    assert isinstance(result.basic, bool)
    assert isinstance(result.e2ee, bool)
    assert result.e2ee_check_mode in ("hasattr", "olm_import", "unchecked")


def test_nio_availability_is_frozen() -> None:
    """NioAvailability dataclass is immutable."""
    availability = NioAvailability(
        basic=True, e2ee=False, e2ee_check_mode="hasattr"
    )
    with pytest.raises(AttributeError):
        availability.basic = False  # type: ignore[misc]
