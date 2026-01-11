"""Tests for Matrix E2EE (End-to-End Encryption) helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from takopi.matrix.crypto import (
    CryptoManager,
    ensure_crypto_store_dir,
    get_default_crypto_store_path,
    is_e2ee_available,
)


class TestIsE2EEAvailable:
    """Test E2EE availability detection."""

    def test_e2ee_available_with_crypto(self) -> None:
        """E2EE is available when nio.crypto exists."""
        # Create a mock nio module with crypto attribute
        mock_nio = MagicMock()
        mock_nio.crypto = MagicMock()
        mock_crypto = MagicMock()
        mock_crypto.Olm = MagicMock()

        with patch.dict("sys.modules", {"nio": mock_nio, "nio.crypto": mock_crypto}):
            result = is_e2ee_available()
            assert result is True

    def test_e2ee_unavailable_no_crypto_attr(self) -> None:
        """E2EE unavailable when nio exists but crypto attr missing."""
        mock_nio = MagicMock(spec=[])  # No crypto attribute
        del mock_nio.crypto  # Ensure it doesn't have crypto

        with patch.dict("sys.modules", {"nio": mock_nio}, clear=False):
            # Need to reload the function or mock hasattr
            with patch("takopi.matrix.crypto.hasattr", return_value=False):
                result = is_e2ee_available()
                assert result is False

    def test_e2ee_unavailable_import_error(self) -> None:
        """E2EE unavailable when nio not installed."""
        # Remove nio from sys.modules if present
        modules_backup = sys.modules.copy()
        sys.modules.pop("nio", None)
        sys.modules.pop("nio.crypto", None)

        with patch.dict("sys.modules", {}, clear=False):
            with patch("builtins.__import__", side_effect=ImportError("nio not found")):
                result = is_e2ee_available()
                assert result is False

        # Restore modules
        sys.modules.update(modules_backup)

    def test_e2ee_unavailable_generic_exception(self) -> None:
        """E2EE unavailable on any exception during check."""
        mock_nio = MagicMock()
        mock_nio.crypto = MagicMock()

        with patch.dict("sys.modules", {"nio": mock_nio}):
            # Importing nio.crypto.Olm raises exception
            with patch(
                "builtins.__import__", side_effect=RuntimeError("Unexpected error")
            ):
                result = is_e2ee_available()
                assert result is False


class TestCryptoStorePath:
    """Test crypto store path utilities."""

    def test_get_default_crypto_store_path(self) -> None:
        """Default crypto store path is in home directory."""
        path = get_default_crypto_store_path()
        assert isinstance(path, Path)
        assert path.name == "matrix_crypto.db"
        assert ".takopi" in str(path)

    def test_ensure_crypto_store_dir_creates_parent(self, tmp_path: Path) -> None:
        """ensure_crypto_store_dir creates parent directory."""
        store_path = tmp_path / "subdir" / "crypto.db"
        assert not store_path.parent.exists()

        ensure_crypto_store_dir(store_path)

        assert store_path.parent.exists()
        assert store_path.parent.is_dir()

    def test_ensure_crypto_store_dir_idempotent(self, tmp_path: Path) -> None:
        """ensure_crypto_store_dir is idempotent."""
        store_path = tmp_path / "crypto.db"
        store_path.parent.mkdir(parents=True, exist_ok=True)

        # Should not raise even if dir exists
        ensure_crypto_store_dir(store_path)
        ensure_crypto_store_dir(store_path)

        assert store_path.parent.exists()


class TestCryptoManager:
    """Test CryptoManager class."""

    def test_init_default_path(self) -> None:
        """CryptoManager uses default path when not specified."""
        manager = CryptoManager()
        assert manager.store_path == get_default_crypto_store_path()
        assert manager._initialized is False

    def test_init_custom_path(self, tmp_path: Path) -> None:
        """CryptoManager accepts custom store path."""
        custom_path = tmp_path / "custom_crypto.db"
        manager = CryptoManager(store_path=custom_path)
        assert manager.store_path == custom_path

    def test_available_property_when_e2ee_available(self) -> None:
        """available property returns True when E2EE available."""
        from takopi.matrix.availability import NioAvailability

        availability = NioAvailability(basic=True, e2ee=True, e2ee_check_mode="olm_import")
        manager = CryptoManager(_nio_availability=availability)
        assert manager.available is True

    def test_available_property_when_e2ee_unavailable(self) -> None:
        """available property returns False when E2EE unavailable."""
        from takopi.matrix.availability import NioAvailability

        availability = NioAvailability(basic=True, e2ee=False, e2ee_check_mode="hasattr")
        manager = CryptoManager(_nio_availability=availability)
        assert manager.available is False

    def test_ensure_store(self, tmp_path: Path) -> None:
        """ensure_store creates crypto store directory."""
        store_path = tmp_path / "subdir" / "crypto.db"
        manager = CryptoManager(store_path=store_path)

        assert not store_path.parent.exists()
        manager.ensure_store()
        assert store_path.parent.exists()

    @pytest.mark.anyio
    async def test_init_crypto_when_unavailable(self) -> None:
        """init_crypto returns False when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = await manager.init_crypto(client)

            assert result is False
            assert manager._initialized is False

    @pytest.mark.anyio
    async def test_init_crypto_not_nio_client(self) -> None:
        """init_crypto returns False for non-nio.AsyncClient."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=True):
            manager = CryptoManager()
            # Not a nio.AsyncClient
            client = "not-a-nio-client"

            result = await manager.init_crypto(client)

            assert result is False

    def test_is_room_encrypted_when_unavailable(self) -> None:
        """is_room_encrypted returns False when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = manager.is_room_encrypted(client, "!room:example.org")

            assert result is False

    def test_is_room_encrypted_not_nio_client(self) -> None:
        """is_room_encrypted returns False for non-nio.AsyncClient."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=True):
            manager = CryptoManager()
            client = "not-a-nio-client"

            result = manager.is_room_encrypted(client, "!room:example.org")

            assert result is False

    @pytest.mark.anyio
    async def test_start_verification_when_unavailable(self) -> None:
        """start_verification returns None when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = await manager.start_verification(client, "DEVICE", "@user:ex.org")

            assert result is None

    @pytest.mark.anyio
    async def test_confirm_verification_when_unavailable(self) -> None:
        """confirm_verification returns False when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = await manager.confirm_verification(client, "txn123")

            assert result is False

    @pytest.mark.anyio
    async def test_cancel_verification_when_unavailable(self) -> None:
        """cancel_verification returns False when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = await manager.cancel_verification(client, "txn123")

            assert result is False

    def test_get_verification_emojis_when_unavailable(self) -> None:
        """get_verification_emojis returns None when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = manager.get_verification_emojis(client, "txn123")

            assert result is None

    @pytest.mark.anyio
    async def test_trust_device_when_unavailable(self) -> None:
        """trust_device returns False when E2EE unavailable."""
        with patch("takopi.matrix.crypto.is_e2ee_available", return_value=False):
            manager = CryptoManager()
            client = MagicMock()

            result = await manager.trust_device(client, "@user:ex.org", "DEVICE")

            assert result is False
