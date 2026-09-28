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


_MASKS: dict[tuple[int, int], list[int]] = {}


def _masks(width: int, k: int) -> list[int]:
    """XOR masks with at most ``k`` bits set, cached."""
    key = (width, k)
    if key not in _MASKS:
        from itertools import combinations

        out = [0]
        for r in range(1, k + 1):
            for bits in combinations(range(width), r):
                m = 0
                for b in bits:
                    m |= 1 << b
                out.append(m)
        _MASKS[key] = out
    return _MASKS[key]


def _layout(n: int, threshold: int) -> tuple[int, int]:
    """Cheapest (blocks, flips-per-block) for the pigeonhole search over ``n`` hashes."""
    from math import comb

    best = None
    for blocks in (2, 4, 8):
        width = 64 // blocks
        k = -(-(threshold + 1) // blocks) - 1  # some block must differ in at most k bits
        probes = sum(comb(width, i) for i in range(k + 1))
        cost = blocks * probes * (1 + n / 2 ** width)
        if best is None or cost < best[0]:
            best = (cost, blocks, k)
    return best[1], best[2]


def cluster(hashes: dict[str, str], threshold: int = 6) -> list[list[str]]:
    """Group ids whose avatar hashes are near-duplicates (single-linkage).

    Near-linear via pigeonhole: the 64 bits are split into equal blocks; two hashes
    within ``threshold`` bits must have some block that differs in at most k bits,
    so each hash is only compared with hashes sharing a block up to k flips. The
    block layout is chosen by estimated cost for this many hashes. Identical photos
    (one stock image on a thousand bots) are grouped outright before the search.
    """
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

    blocks, k = _layout(len(values), threshold)
    width = 64 // blocks
    full = (1 << width) - 1
    index: list[dict[int, list[int]]] = [{} for _ in range(blocks)]
    for idx, v in enumerate(values):
        for b in range(blocks):
            index[b].setdefault((v >> (width * b)) & full, []).append(idx)
    masks = _masks(width, k)
    for idx, v in enumerate(values):
        seen: set[int] = set()
        for b in range(blocks):
            block, bucket = (v >> (width * b)) & full, index[b]
            for m in masks:
                for other in bucket.get(block ^ m, ()):
                    if other <= idx or other in seen:
                        continue
                    seen.add(other)
                    if bin(v ^ values[other]).count("1") <= threshold:
                        parent[find(idx)] = find(other)
    groups: dict[int, list[str]] = {}
    for idx, v in enumerate(values):
        groups.setdefault(find(idx), []).extend(by_value[v])
    return [sorted(g) for g in groups.values() if len(g) > 1]
