"""
Unit tests for sprite_extractor.py and sprite_injector.py — TILE format codec.
"""

import struct
import pytest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from sprite_extractor import decode_tile, u16, u32
from sprite_injector import encode_tile, _encode_row


# ─── Helpers ────────────────────────────────────────────────────────────────

def build_tile(height, width, rows_segments, palette_id=0):
    """
    Build a minimal valid TILE binary from segment descriptions.

    rows_segments: list of [(x_start, [pixel_indices]), ...] per row.
    Returns raw TILE bytes.
    """
    # Encode each row
    row_blobs = []
    for segments in rows_segments:
        if not segments:
            # Empty row — fully transparent
            row_blobs.append(struct.pack("<HBB", 0, 0, 0x80))
        else:
            parts = []
            for i, (x_pos, pixels) in enumerate(segments):
                is_last = (i == len(segments) - 1)
                flags = 0x80 if is_last else 0x00
                count = len(pixels)
                part = struct.pack("<HBB", x_pos, count, flags) + bytes(pixels)
                parts.append(part)
            row_blobs.append(b''.join(parts))

    # Build offset table
    table_size = height * 4
    offsets = []
    current = table_size
    for blob in row_blobs:
        offsets.append(current)
        current += len(blob)

    # Header: 16 bytes (version=3, height, then 6 more u16 words)
    header = struct.pack("<HHHHHHHH", 3, height, 0, 0, 32, 0, 0, 1)
    padding = b'\x00' * 6
    pal_bytes = struct.pack("<I", palette_id)
    offset_table = b''.join(struct.pack("<I", o) for o in offsets)
    row_data = b''.join(row_blobs)

    return header + padding + pal_bytes + offset_table + row_data


# ─── Tests: decode_tile ────────────────────────────────────────────────────

class TestDecodeTile:
    def test_basic_decode(self):
        """Decode a simple 2-row tile with one segment each."""
        rows = [
            [(0, [1, 2, 3, 4])],    # row 0: pixels at x=0..3
            [(2, [5, 6])],           # row 1: pixels at x=2..3
        ]
        tile = build_tile(2, 4, rows, palette_id=42)
        result = decode_tile(tile)

        assert result is not None
        assert result["height"] == 2
        assert result["palette_id"] == 42
        assert result["rows"][0] == [(0, [1, 2, 3, 4])]
        assert result["rows"][1] == [(2, [5, 6])]

    def test_width_calculated_from_segments(self):
        """Width is the max(x_pos + count) across all segments."""
        rows = [
            [(10, [1, 2, 3])],  # extends to x=13
            [(0, [1])],         # extends to x=1
        ]
        tile = build_tile(2, 13, rows)
        result = decode_tile(tile)

        assert result["width"] == 13

    def test_multi_segment_row(self):
        """Rows can have multiple non-contiguous segments."""
        rows = [
            [(0, [1, 2]), (5, [3, 4, 5])],  # two segments with gap
        ]
        tile = build_tile(1, 8, rows)
        result = decode_tile(tile)

        assert len(result["rows"][0]) == 2
        assert result["rows"][0][0] == (0, [1, 2])
        assert result["rows"][0][1] == (5, [3, 4, 5])

    def test_transparent_row(self):
        """Fully transparent rows produce empty segment list."""
        rows = [
            [(0, [1, 2, 3])],
            [],  # transparent row
            [(0, [4, 5])],
        ]
        tile = build_tile(3, 3, rows)
        result = decode_tile(tile)

        assert result["height"] == 3
        assert result["rows"][0] == [(0, [1, 2, 3])]
        assert result["rows"][1] == []  # transparent
        assert result["rows"][2] == [(0, [4, 5])]

    def test_palette_id_preserved(self):
        """Different palette IDs are correctly read."""
        for pal_id in [0, 1, 100, 853, 65535]:
            tile = build_tile(1, 1, [[(0, [1])]], palette_id=pal_id)
            result = decode_tile(tile)
            assert result["palette_id"] == pal_id

    def test_version_check(self):
        """Non-version-3 tiles return None."""
        tile = build_tile(1, 1, [[(0, [1])]])
        # Corrupt version to 2
        bad = bytearray(tile)
        bad[0] = 2
        bad[1] = 0
        assert decode_tile(bytes(bad)) is None

    def test_too_short_returns_none(self):
        """Data shorter than 26 bytes returns None."""
        assert decode_tile(b"\x03\x00" + b"\x00" * 10) is None
        assert decode_tile(b"") is None

    def test_large_sprite(self):
        """Decode a larger sprite (many rows)."""
        height = 64
        rows = [[(0, list(range(1, 33)))] for _ in range(height)]
        tile = build_tile(height, 32, rows, palette_id=5)
        result = decode_tile(tile)

        assert result["height"] == 64
        assert result["width"] == 32
        assert len(result["rows"]) == 64
        assert result["rows"][0] == [(0, list(range(1, 33)))]

    def test_pixel_values_full_range(self):
        """Pixel values 1-255 are preserved (0 is transparent)."""
        pixels = list(range(1, 256))  # 255 pixels
        rows = [[(0, pixels)]]
        tile = build_tile(1, 255, rows)
        result = decode_tile(tile)
        assert result["rows"][0] == [(0, pixels)]


# ─── Tests: _encode_row ───────────────────────────────────────────────────

class TestEncodeRow:
    def test_simple_row(self):
        """Encode a row with contiguous opaque pixels."""
        row = np.array([1, 2, 3, 4, 0, 0], dtype=np.uint8)
        blob = _encode_row(row)

        # Should produce: [x=0, count=4, flags=0x80, pixels 1,2,3,4]
        assert blob == struct.pack("<HBB", 0, 4, 0x80) + bytes([1, 2, 3, 4])

    def test_multiple_segments(self):
        """Encode a row with a transparent gap creating two segments."""
        row = np.array([1, 2, 0, 0, 3, 4], dtype=np.uint8)
        blob = _encode_row(row)

        # Two segments: x=0 count=2 flags=0x00, x=4 count=2 flags=0x80
        expected = (
            struct.pack("<HBB", 0, 2, 0x00) + bytes([1, 2]) +
            struct.pack("<HBB", 4, 2, 0x80) + bytes([3, 4])
        )
        assert blob == expected

    def test_fully_transparent_row(self):
        """All-zero row produces a minimal empty segment."""
        row = np.array([0, 0, 0, 0], dtype=np.uint8)
        blob = _encode_row(row)

        # Zero-length segment with last flag
        assert blob == struct.pack("<HBB", 0, 0, 0x80)

    def test_leading_transparency(self):
        """Transparent pixels at the start are skipped."""
        row = np.array([0, 0, 5, 6, 7], dtype=np.uint8)
        blob = _encode_row(row)

        assert blob == struct.pack("<HBB", 2, 3, 0x80) + bytes([5, 6, 7])

    def test_trailing_transparency(self):
        """Transparent pixels at the end are skipped."""
        row = np.array([1, 2, 0, 0, 0], dtype=np.uint8)
        blob = _encode_row(row)

        assert blob == struct.pack("<HBB", 0, 2, 0x80) + bytes([1, 2])

    def test_single_pixel(self):
        """A single opaque pixel is encoded correctly."""
        row = np.array([0, 0, 42, 0, 0], dtype=np.uint8)
        blob = _encode_row(row)

        assert blob == struct.pack("<HBB", 2, 1, 0x80) + bytes([42])

    def test_magenta_indices_preserved(self):
        """Palette indices 248-255 (shadow/blend) are real pixels, not transparent."""
        row = np.array([248, 249, 250, 255], dtype=np.uint8)
        blob = _encode_row(row)

        assert blob == struct.pack("<HBB", 0, 4, 0x80) + bytes([248, 249, 250, 255])


# ─── Tests: encode_tile ───────────────────────────────────────────────────

class TestEncodeTile:
    def test_basic_encode(self):
        """Encode a small pixel array to TILE format."""
        pixels = np.array([
            [1, 2, 3],
            [0, 4, 5],
        ], dtype=np.uint8)

        tile_data = encode_tile(pixels, palette_id=10)

        # Verify header
        assert u16(tile_data, 0) == 3   # version
        assert u16(tile_data, 2) == 2   # height
        assert u32(tile_data, 22) == 10  # palette_id

    def test_encode_decode_roundtrip(self):
        """encode → decode produces same pixel content."""
        pixels = np.array([
            [0, 1, 2, 3, 0],
            [0, 0, 4, 5, 6],
            [7, 8, 0, 0, 9],
        ], dtype=np.uint8)

        tile_data = encode_tile(pixels, palette_id=42)
        decoded = decode_tile(tile_data)

        assert decoded is not None
        assert decoded["height"] == 3
        assert decoded["palette_id"] == 42

        # Reconstruct pixel array from decoded segments
        h, w = decoded["height"], decoded["width"]
        result = np.zeros((h, w), dtype=np.uint8)
        for y, segments in enumerate(decoded["rows"]):
            for x_start, px_list in segments:
                for dx, idx in enumerate(px_list):
                    result[y, x_start + dx] = idx

        # Compare (result may be wider due to width calculation)
        for y in range(pixels.shape[0]):
            for x in range(pixels.shape[1]):
                assert result[y, x] == pixels[y, x], f"Mismatch at ({y},{x})"

    def test_all_transparent(self):
        """Fully transparent image produces valid but empty TILE."""
        pixels = np.zeros((4, 4), dtype=np.uint8)
        tile_data = encode_tile(pixels, palette_id=0)
        decoded = decode_tile(tile_data)

        assert decoded is not None
        assert decoded["height"] == 4
        # All rows should be empty (transparent)
        for row in decoded["rows"]:
            assert row == []

    def test_solid_fill(self):
        """Solid non-transparent fill encodes correctly."""
        pixels = np.full((3, 5), 100, dtype=np.uint8)
        tile_data = encode_tile(pixels, palette_id=7)
        decoded = decode_tile(tile_data)

        assert decoded is not None
        assert decoded["height"] == 3
        for row in decoded["rows"]:
            assert len(row) == 1
            assert row[0] == (0, [100, 100, 100, 100, 100])

    def test_header_fields_preserved(self):
        """Custom header fields are encoded correctly."""
        pixels = np.array([[1]], dtype=np.uint8)
        tile_data = encode_tile(pixels, palette_id=99,
                                header_w2=11, header_w3=22,
                                header_w4=33, header_w5=44,
                                header_w6=55, header_w7=66)

        assert u16(tile_data, 4) == 11   # w2
        assert u16(tile_data, 6) == 22   # w3
        assert u16(tile_data, 8) == 33   # w4
        assert u16(tile_data, 10) == 44  # w5
        assert u16(tile_data, 12) == 55  # w6
        assert u16(tile_data, 14) == 66  # w7

    def test_large_sprite_roundtrip(self):
        """Larger sprite (64x64) roundtrips correctly."""
        rng = np.random.default_rng(42)
        # Create a random sprite with transparent background and opaque center
        pixels = np.zeros((64, 64), dtype=np.uint8)
        pixels[10:54, 10:54] = rng.integers(1, 256, size=(44, 44), dtype=np.uint8)

        tile_data = encode_tile(pixels, palette_id=200)
        decoded = decode_tile(tile_data)

        assert decoded is not None
        assert decoded["height"] == 64

        # Reconstruct and compare
        h, w = decoded["height"], decoded["width"]
        result = np.zeros((h, max(w, 64)), dtype=np.uint8)
        for y, segments in enumerate(decoded["rows"]):
            for x_start, px_list in segments:
                for dx, idx in enumerate(px_list):
                    result[y, x_start + dx] = idx

        np.testing.assert_array_equal(result[:64, :64], pixels)

    def test_checkerboard_pattern(self):
        """Alternating transparent/opaque pixels create many segments."""
        # [1, 0, 2, 0, 3, 0, 4, 0] — 4 segments
        pixels = np.array([[1, 0, 2, 0, 3, 0, 4, 0]], dtype=np.uint8)
        tile_data = encode_tile(pixels, palette_id=0)
        decoded = decode_tile(tile_data)

        assert decoded is not None
        row = decoded["rows"][0]
        assert len(row) == 4
        assert row[0] == (0, [1])
        assert row[1] == (2, [2])
        assert row[2] == (4, [3])
        assert row[3] == (6, [4])


# ─── Tests: Full encode-decode identity on constructed data ─────────────────

class TestRoundtripConstructed:
    def test_build_decode_identity(self):
        """build_tile → decode_tile → encode_tile → decode_tile gives same pixels."""
        segments = [
            [(0, [10, 20, 30]), (5, [40, 50])],
            [(1, [60, 70, 80, 90])],
            [],
        ]
        tile = build_tile(3, 7, segments, palette_id=100)
        decoded = decode_tile(tile)

        # Reconstruct pixels
        h, w = decoded["height"], decoded["width"]
        pixels = np.zeros((h, w), dtype=np.uint8)
        for y, segs in enumerate(decoded["rows"]):
            for x_start, px_list in segs:
                for dx, idx in enumerate(px_list):
                    pixels[y, x_start + dx] = idx

        # Re-encode
        reencoded = encode_tile(pixels, decoded["palette_id"])
        decoded2 = decode_tile(reencoded)

        # Reconstruct again
        h2, w2 = decoded2["height"], decoded2["width"]
        pixels2 = np.zeros((h2, max(w2, w)), dtype=np.uint8)
        for y, segs in enumerate(decoded2["rows"]):
            for x_start, px_list in segs:
                for dx, idx in enumerate(px_list):
                    pixels2[y, x_start + dx] = idx

        np.testing.assert_array_equal(pixels2[:h, :w], pixels)


# ─── Tests: Real game data ─────────────────────────────────────────────────

class TestRealSprites:
    """Tests against actual maindata.cam sprites (skipped if not present)."""

    @pytest.fixture
    def maindata(self):
        path = Path(__file__).parent.parent / "Data" / "maindata.cam"
        if not path.exists():
            pytest.skip("Data/maindata.cam not available")
        from cam_reader import read_cam
        cam_data = path.read_bytes()
        sections = read_cam(cam_data)
        return cam_data, sections

    def test_decode_first_10_tiles(self, maindata):
        """First 10 TILE entries decode without error."""
        cam_data, sections = maindata
        tile_section = sections[1]  # TILE is section index 1

        for i in range(min(10, len(tile_section.files))):
            f = tile_section.files[i]
            data = cam_data[f.data_off:f.data_off + f.data_size]
            result = decode_tile(data)
            # Some entries might not be version 3, which returns None — that's ok
            if result is not None:
                assert result["height"] > 0
                assert len(result["rows"]) == result["height"]

    def test_roundtrip_sample_tiles(self, maindata):
        """Sample TILE entries survive encode → decode pixel comparison."""
        cam_data, sections = maindata
        tile_section = sections[1]

        # Test a variety of tile indices
        test_indices = [0, 100, 500, 1000, 3547, 5000]
        passed = 0

        for idx in test_indices:
            if idx >= len(tile_section.files):
                continue

            f = tile_section.files[idx]
            original = cam_data[f.data_off:f.data_off + f.data_size]
            decoded = decode_tile(original)

            if decoded is None:
                continue  # Not version 3

            # Reconstruct pixels
            h, w = decoded["height"], decoded["width"]
            if w == 0 or h == 0:
                continue

            pixels = np.zeros((h, w), dtype=np.uint8)
            for y, segments in enumerate(decoded["rows"]):
                for x_start, px_list in segments:
                    for dx, idx_val in enumerate(px_list):
                        pixels[y, x_start + dx] = idx_val

            # Re-encode
            reencoded = encode_tile(
                pixels, decoded["palette_id"],
                header_w2=u16(original, 4),
                header_w3=u16(original, 6),
                header_w4=u16(original, 8),
                header_w5=u16(original, 10),
                header_w6=u16(original, 12),
                header_w7=u16(original, 14),
            )

            # Decode re-encoded
            decoded2 = decode_tile(reencoded)
            assert decoded2 is not None

            # Compare pixel content
            pixels2 = np.zeros((h, w), dtype=np.uint8)
            for y, segments in enumerate(decoded2["rows"]):
                for x_start, px_list in segments:
                    for dx, idx_val in enumerate(px_list):
                        if x_start + dx < w:
                            pixels2[y, x_start + dx] = idx_val

            np.testing.assert_array_equal(pixels2, pixels,
                                          err_msg=f"Pixel mismatch on TILE[{idx}]")
            passed += 1

        assert passed > 0, "No valid tiles found to test"

    def test_palette_ids_valid(self, maindata):
        """TILE palette_ids reference valid SPLT entries."""
        cam_data, sections = maindata
        tile_section = sections[1]
        splt_section = sections[2]
        max_palette = len(splt_section.files) - 1

        # Check first 100 tiles
        for i in range(min(100, len(tile_section.files))):
            f = tile_section.files[i]
            data = cam_data[f.data_off:f.data_off + f.data_size]
            decoded = decode_tile(data)
            if decoded is not None:
                assert decoded["palette_id"] <= max_palette, \
                    f"TILE[{i}] palette_id {decoded['palette_id']} > max {max_palette}"
