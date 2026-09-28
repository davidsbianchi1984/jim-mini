"""Perceptual image hashing for shared-photo clusters and clone detection.

A difference hash (dHash) survives resizing, recompression and small colour
shifts, which is exactly what happens when a bot operator reuses one stolen
photo across many accounts or copies a friend's profile picture.

Hashes are stored as 16-character hex strings (64 bits). Only the hash is kept;
the avatar itself is never stored.
"""
from __future__ import annotations

from typing import Sequence


def dhash_from_pixels(pixels: Sequence[Sequence[float]], size: int = 8) -> str:
    """dHash of a grayscale image given as rows of pixel values.

    The image is box-resampled to (size+1) x size, then each bit records whether
    a pixel is brighter than its right-hand neighbour.
    """
    h = len(pixels)
    w = len(pixels[0]) if h else 0
    if h == 0 or w == 0:
        raise ValueError("empty image")
    cols, rows = size + 1, size
    small: list[list[float]] = []
    for r in range(rows):
        y0, y1 = r * h // rows, max((r + 1) * h // rows, r * h // rows + 1)
        row: list[float] = []
        for c in range(cols):
            x0, x1 = c * w // cols, max((c + 1) * w // cols, c * w // cols + 1)
            total, n = 0.0, 0
            for y in range(y0, min(y1, h)):
                for x in range(x0, min(x1, w)):
                    total += pixels[y][x]
                    n += 1
            row.append(total / max(n, 1))
        small.append(row)
    bits = 0
    for r in range(rows):
        for c in range(size):
            bits = (bits << 1) | (1 if small[r][c] > small[r][c + 1] else 0)
    return f"{bits:0{size * size // 4}x}"


def dhash_from_bytes(data: bytes) -> str:
    """dHash of an encoded image (PNG/JPEG). Needs Pillow."""
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Pillow is required to hash image bytes") from exc
    import io

    img = Image.open(io.BytesIO(data)).convert("L").resize((9, 8))
    px = list(img.getdata())
    rows = [px[i * 9:(i + 1) * 9] for i in range(8)]
    return dhash_from_pixels(rows)


def hamming(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def similar(a: str | None, b: str | None, threshold: int = 10) -> bool:
    """True when two avatar hashes are near-duplicates (<= threshold differing bits)."""
    if not a or not b:
        return False
    return hamming(a, b) <= threshold


def cluster(hashes: dict[str, str], threshold: int = 6) -> list[list[str]]:
    """Group ids whose avatar hashes are near-duplicates (single-linkage).

    Pigeonhole banding keeps this near-linear: split the 64 bits into
    ``threshold + 1`` bands; two hashes within ``threshold`` bits must agree
    exactly on at least one band, so only ids sharing a band are compared.
    """
    # Identical photos (one stock image on a thousand bots) are grouped outright;
    # only the distinct hash values go through the near-duplicate search.
    by_value: dict[int, list[str]] = {}
    for i, h in hashes.items():
        by_value.setdefault(int(h, 16), []).append(i)
    values = list(by_value)
    parent = list(range(len(values)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    bands = threshold + 1
    edges = [round(64 * b / bands) for b in range(bands + 1)]
    compared: set[tuple[int, int]] = set()
    for b in range(bands):
        lo, hi = edges[b], edges[b + 1]
        mask = ((1 << (hi - lo)) - 1) << lo
        buckets: dict[int, list[int]] = {}
        for idx, v in enumerate(values):
            buckets.setdefault(v & mask, []).append(idx)
        for members in buckets.values():
            for x, a in enumerate(members):
                for c in members[x + 1:]:
                    if (a, c) in compared:
                        continue
                    compared.add((a, c))
                    if bin(values[a] ^ values[c]).count("1") <= threshold:
                        parent[find(a)] = find(c)
    groups: dict[int, list[str]] = {}
    for idx, v in enumerate(values):
        groups.setdefault(find(idx), []).extend(by_value[v])
    return [sorted(g) for g in groups.values() if len(g) > 1]
