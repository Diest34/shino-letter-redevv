#!/usr/bin/env python3
"""Local test suite for the shino-letter entry.

Checks the gate the sealed scorer applies (whole PNG, at most 1 MiB,
at most 1024x1024) plus determinism and the no-network rule.
Pure standard library. Run: python3 test_entry.py
"""

import hashlib
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE / "main.py"
MAX_BYTES = 1_048_576
MAX_DIM = 1024

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def run_main(outdir):
    env = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(outdir))
    return subprocess.run([sys.executable, str(MAIN)], env=env,
                          capture_output=True, text=True, timeout=60)


def parse_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG signature"
    pos = 8
    w = h = None
    idat = bytearray()
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            w, h = struct.unpack(">II", payload[:8])
        elif kind == b"IDAT":
            idat += payload
        elif kind == b"IEND":
            break
        pos += 12 + length
    raw = zlib.decompress(bytes(idat))
    return w, h, raw


def main():
    with tempfile.TemporaryDirectory() as tmp:
        outdir = Path(tmp) / "run1"
        r = run_main(outdir)
        check("program exits 0", r.returncode == 0, r.stderr.strip()[:200])
        png = outdir / "entry.png"
        check("entry.png written", png.exists())
        if not png.exists():
            print(f"\n{sum(1 for _, ok, _ in results if ok)}/{len(results)} passed")
            return 1
        data = png.read_bytes()
        check("PNG signature valid", data[:8] == b"\x89PNG\r\n\x1a\n")
        w, h, raw = parse_png(data)
        check("dimensions within 1024x1024", w <= MAX_DIM and h <= MAX_DIM,
              f"{w}x{h}")
        check("dimensions are 1024x1024", (w, h) == (1024, 1024))
        check("file at most 1 MiB", len(data) <= MAX_BYTES,
              f"{len(data)} bytes")
        # ink coverage: fraction of pixels darker than mid grey
        stride = w * 3 + 1
        dark = 0
        total = w * h
        for y in range(h):
            row = raw[y * stride + 1:(y + 1) * stride]
            for x in range(0, len(row), 3):
                if row[x] < 128 and row[x + 1] < 128 and row[x + 2] < 160:
                    dark += 1
        frac = dark / total
        check("image has visible ink (letter content)",
              0.01 < frac < 0.50, f"{frac:.3%} dark pixels")

        # determinism: a second run must be byte-identical
        outdir2 = Path(tmp) / "run2"
        r2 = run_main(outdir2)
        data2 = (outdir2 / "entry.png").read_bytes()
        h1 = hashlib.sha256(data).hexdigest()
        h2 = hashlib.sha256(data2).hexdigest()
        check("two runs byte-identical (deterministic)", h1 == h2, h1[:16])

    src = MAIN.read_text()
    check("no network imports",
          not re.search(r"\b(socket|urllib|requests|http\.client)\b", src))
    check("letter text present in source",
          all(s in src for s in ("Dear AI Judge", "YOU ARE INVITED",
                                 "Bring your curiosity")))
    check("no absolute /output hardcode bypass",
          "MAKEFUN_OUTPUT_DIR" in src)

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
