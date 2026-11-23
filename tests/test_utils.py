"""Tests for utility functions."""
import os
import tempfile
from pathlib import Path

import pytest

from scripts.core.utils import (
    get_project_dir,
    get_chrome_profile_dir,
    ensure_dir,
    validate_account,
    clean_chrome_locks,
    get_valid_media_paths,
    sanitize_filename,
    parse_media_paths,
    format_media_paths,
    generate_short_id,
    normalize_path,
    is_subpath,
    RateLimiter,
    find_unassigned_media,
    get_media_list,
)


class TestPathUtilities:
    """Test path-related utilities."""

    def test_get_project_dir(self):
        """Test project directory resolution."""
        proj_dir = get_project_dir()
        assert proj_dir.name == "resrise-studio"
        assert (proj_dir / "scripts").exists()

    def test_get_chrome_profile_dir(self):
        """Test Chrome profile directory generation."""
        profile_dir = get_chrome_profile_dir("avanyamehra")
        assert "avanyamehra" in str(profile_dir)
        assert "User Data - Automation" in str(profile_dir)

    def test_ensure_dir_creates(self, tmp_path):
        """Test ensure_dir creates directory."""
        new_dir = tmp_path / "new" / "nested" / "dir"
        result = ensure_dir(new_dir)
        assert result.exists()
        assert result.is_dir()
        assert result == new_dir

    def test_ensure_dir_existing(self, tmp_path):
        """Test ensure_dir with existing directory."""
        existing = tmp_path / "existing"
        existing.mkdir()
        result = ensure_dir(existing)
        assert result == existing


class TestAccountValidation:
    """Test account validation."""

    def test_validate_account_valid(self):
        """Test valid account handles."""
        assert validate_account("avanyamehra") == "avanyamehra"
        assert validate_account("@avanyamehra") == "avanyamehra"
        assert validate_account("  @mairamehraofficial  ") == "mairamehraofficial"
        assert validate_account("IAMGAGANKUMAR") == "iamgagankumar"

    def test_validate_account_invalid(self):
        """Test invalid account handles raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported account"):
            validate_account("invalid_account")

        with pytest.raises(ValueError, match="Unsupported account"):
            validate_account("@notreal")


class TestChromeLockCleanup:
    """Test Chrome lock file cleanup."""

    def test_clean_chrome_locks(self, tmp_path):
        """Test removal of Chrome lock files."""
        lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]
        for lf in lock_files:
            (tmp_path / lf).write_text("lock")

        clean_chrome_locks(tmp_path)

        for lf in lock_files:
            assert not (tmp_path / lf).exists()

    def test_clean_chrome_locks_missing(self, tmp_path):
        """Test cleanup with missing lock files (should not raise)."""
        clean_chrome_locks(tmp_path)  # Should not raise


class TestMediaPaths:
    """Test media path utilities."""

    def test_get_valid_media_paths(self, tmp_path):
        """Test filtering valid media paths."""
        existing = tmp_path / "exists.jpg"
        existing.write_text("content")

        paths = [
            str(existing),
            str(tmp_path / "missing.jpg"),
            "",
            str(tmp_path / "also_exists.png"),
        ]
        (tmp_path / "also_exists.png").write_text("content")

        valid = get_valid_media_paths(paths)
        assert len(valid) == 2
        assert str(existing) in valid
        assert str(tmp_path / "also_exists.png") in valid

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("normal_file.jpg") == "normal_file.jpg"
        assert sanitize_filename('file<>:"/\\|?*.jpg') == "file.jpg"
        assert sanitize_filename("a" * 300 + ".jpg") == "a" * 251 + ".jpg"

    def test_parse_media_paths(self):
        """Test parsing media paths from textarea."""
        raw = "path1.jpg\npath2.png\n\npath3.webp\n"
        parsed = parse_media_paths(raw)
        assert parsed == ["path1.jpg", "path2.png", "path3.webp"]

    def test_format_media_paths(self):
        """Test formatting media paths for textarea."""
        paths = ["path1.jpg", "path2.png"]
        formatted = format_media_paths(paths)
        assert formatted == "path1.jpg\npath2.png"

    def test_generate_short_id(self):
        """Test short ID generation."""
        id1 = generate_short_id()
        id2 = generate_short_id()
        assert len(id1) == 8
        assert len(id2) == 8
        assert id1 != id2

        # Custom length
        id3 = generate_short_id(12)
        assert len(id3) == 12

    def test_normalize_path(self, tmp_path):
        """Test path normalization."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        normalized = normalize_path(str(test_file))
        assert normalized == str(test_file.resolve())

    def test_is_subpath(self, tmp_path):
        """Test path traversal protection."""
        parent = tmp_path / "parent"
        parent.mkdir(parents=True, exist_ok=True)
        child = parent / "child" / "file.txt"
        child.parent.mkdir(parents=True, exist_ok=True)
        child.write_text("content")

        assert is_subpath(child, parent) is True
        assert is_subpath(parent, child) is False
        assert is_subpath(tmp_path / "outside.txt", parent) is False
        # Test with non-existent child path (should still work)
        assert is_subpath(tmp_path / "nonexistent", parent) is False


class TestRateLimiter:
    """Test token bucket rate limiter."""

    def test_acquire_available(self):
        """Test acquiring tokens when available."""
        limiter = RateLimiter(rate=10, burst=5)  # 10/sec, burst 5
        assert limiter.acquire(3) is True
        assert limiter.acquire(2) is True

    def test_acquire_exhausted_blocking(self):
        """Test blocking acquire when exhausted."""
        import time
        limiter = RateLimiter(rate=100, burst=2)  # Fast rate for testing

        assert limiter.acquire(2) is True
        start = time.monotonic()
        result = limiter.acquire(1, blocking=True)
        elapsed = time.monotonic() - start
        assert result is True
        assert elapsed >= 0.01  # Should have waited

    def test_acquire_exhausted_nonblocking(self):
        """Test non-blocking acquire when exhausted."""
        limiter = RateLimiter(rate=1, burst=1)
        assert limiter.acquire(1) is True
        assert limiter.acquire(1, blocking=False) is False


class TestQueueUtilities:
    """Test queue-related utilities."""

    def test_find_unassigned_media(self, tmp_path, monkeypatch):
        """Test finding unassigned media files."""
        # Create draft media dir structure
        acc_dir = tmp_path / "draft_media" / "avanyamehra"
        acc_dir.mkdir(parents=True)

        slide1 = acc_dir / "slide1.jpg"
        slide2 = acc_dir / "slide2.jpg"
        slide3 = acc_dir / "slide3.png"

        slide1.write_text("img1")
        slide2.write_text("img2")
        slide3.write_text("img3")

        # Queue with one item using slide1
        queue = [{
            "media_paths": [str(slide1)]
        }]

        # Patch get_settings in both config and utils modules
        import scripts.core.config as config_module
        import scripts.core.utils as utils_module

        class MockSettings:
            draft_media_dir = tmp_path / "draft_media"

        monkeypatch.setattr(config_module, "get_settings", lambda: MockSettings())
        monkeypatch.setattr(utils_module, "get_settings", lambda: MockSettings())

        from scripts.core.utils import find_unassigned_media
        found = find_unassigned_media("avanyamehra", queue, max_files=10)
        assert len(found) == 2, f"Expected 2 files, got {len(found)}: {found}"
        assert any("slide2.jpg" in f for f in found)
        assert any("slide3.png" in f for f in found)

    def test_get_media_list_from_media_paths(self):
        """Test get_media_list with media_paths list."""
        item = {"media_paths": ["path1.jpg", "path2.png", ""]}
        result = get_media_list(item)
        assert result == ["path1.jpg", "path2.png"]

    def test_get_media_list_from_media_path(self):
        """Test get_media_list with single media_path."""
        item = {"media_path": "single.jpg"}
        result = get_media_list(item)
        assert result == ["single.jpg"]

    def test_get_media_list_empty(self):
        """Test get_media_list with no media."""
        item = {}
        result = get_media_list(item)
        assert result == []

    def test_get_media_list_none(self):
        """Test get_media_list with None paths."""
        item = {"media_paths": None}
        result = get_media_list(item)
        assert result == []