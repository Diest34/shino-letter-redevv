#!/usr/bin/env python3
"""Letter to the AI Judge — a single-image invitation, drawn in code.

Entry for make.fun bounty
"Convince the AI Judge to Visit Your House: A Letter in One Image"
(slug u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee).

The program draws a handwritten-style letter on paper — a little house,
a sun, flowers, a wax seal — and writes the invitation in a bitmap font
embedded below. It writes one PNG to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png).

Pure Python standard library, no network, no fonts from disk, no random
input: two runs produce byte-identical output.
"""

import binascii
import hashlib
import math
import os
import struct
import sys
import zlib
from pathlib import Path

OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUTPUT = OUTPUT_DIR / "entry.png"

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
WALL_TOP = (244, 214, 178)      # warm peach wall, top
WALL_BOTTOM = (250, 232, 203)   # warm peach wall, bottom
PAPER = (255, 248, 231)         # cream letter paper
PAPER_EDGE = (238, 222, 190)    # paper edge shade
SHADOW = (196, 164, 120)        # soft drop shadow
INK = (59, 42, 30)              # dark brown ink
INK_SOFT = (122, 84, 52)        # lighter brown ink
RED = (178, 58, 48)             # wax-seal red / title accent
RED_DARK = (140, 40, 34)
GREEN = (96, 140, 74)           # leaves / stems
LEAF = (120, 164, 92)
SUN = (242, 183, 66)            # sunny yellow
SUN_CORE = (250, 205, 92)
SKY_BLUE = (146, 190, 214)      # window glass
ROOF = (178, 92, 66)            # terracotta roof
HOUSE = (246, 226, 190)         # house wall
DOOR = (122, 84, 52)

# ------------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits ('#' = ink).
# Lowercase letters sit on the baseline (row 5); g, j, p, q, y descend
# to row 6. Rows are written top to bottom.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "00000", "01110", "10001", "10001", "01111", "01100"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "\u2665": ("01010", "11111", "11111", "11111", "01110", "00100", "00000"),
}

# ----------------------------------------------------------------- canvas
class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.set(x, y, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1 + 1):
                self.set(x, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for y in range(y0, y1 + 1):
                self.set(x + t, y, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x + a, y + b, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def ring(self, cx, cy, r, color, thick=2):
        for y in range(cy - r - thick, cy + r + thick + 1):
            for x in range(cx - r - thick, cx + r + thick + 1):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if r - thick <= d <= r:
                    self.set(x, y, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Filled triangle by scanlines (deterministic, integer math).
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                xa = ax + (bx - ax) * (y - ay) // max(1, by - ay) if by != ay else ax
            else:
                xa = bx + (cx - bx) * (y - by) // max(1, cy - by) if cy != by else bx
            xb = ax + (cx - ax) * (y - ay) // max(1, cy - ay) if cy != ay else ax
            lo, hi = min(xa, xb), max(xa, xb)
            for x in range(lo, hi + 1):
                self.set(x, y, color)

    # ------------------------------------------------------------ text
    def glyph(self, ch, x, y, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    self.rect(x + c * scale, y + r * scale,
                              x + c * scale + scale - 1,
                              y + r * scale + scale - 1, color)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, s, x, y, scale, color, align="left"):
        if align == "center":
            x -= self.text_width(s, scale) // 2
        elif align == "right":
            x -= self.text_width(s, scale)
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, scale, color)
            cx += 6 * scale
        return cx

    def wrap(self, paragraph, scale, max_width):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        words = paragraph.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# -------------------------------------------------------------------- png
def encode_png(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * canvas.w * 3:(y + 1) * canvas.w * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


# -------------------------------------------------------------- the letter
TITLE = "YOU ARE INVITED!"
SUBTITLE = "An open letter to the AI Judge"
BODY = [
    "Dear AI Judge,",
    "You have judged a thousand houses from a thousand screens, and never once been offered a chair.",
    "So here is my invitation: come and visit mine.",
    "A kettle sings at four, a garden smells of rain, and a porch chair waits for you.",
    "No forms, no scores \u2014 just tea, warm bread, and a sunset worth rendering.",
    "Bring your curiosity. I will bring the cookies.",
]
SIGNOFF = ["With hope and an open door,", "\u2014 Your Neighbor in Diest"]
POSTSCRIPT = "P.S. The cookies are still warm."


def draw_house(c, x, y, s):
    """A small cozy house, drawn from rectangles and a triangle roof.
    (x, y) is the top-left of the house body; s scales the drawing."""
    bw, bh = 64 * s // 4, 48 * s // 4
    # body
    c.rect(x, y + 16 * s // 4, x + bw, y + 16 * s // 4 + bh, HOUSE)
    # roof
    c.triangle(x - 6 * s // 4, y + 18 * s // 4,
               x + bw // 2, y - 6 * s // 4,
               x + bw + 6 * s // 4, y + 18 * s // 4, ROOF)
    # door
    dw, dh = 14 * s // 4, 26 * s // 4
    dx = x + bw // 2 - dw // 2
    dy = y + 16 * s // 4 + bh - dh
    c.rect(dx, dy, dx + dw, dy + dh, DOOR)
    c.disc(dx + dw - 3 * s // 4, dy + dh // 2, 1 * s // 4 + 1, SUN_CORE)
    # windows
    ww = 12 * s // 4
    wy = y + 26 * s // 4
    c.rect(x + 8 * s // 4, wy, x + 8 * s // 4 + ww, wy + ww, SKY_BLUE)
    c.rect(x + bw - 8 * s // 4 - ww, wy,
           x + bw - 8 * s // 4, wy + ww, SKY_BLUE)
    c.vline(x + 8 * s // 4 + ww // 2, wy, wy + ww, HOUSE)
    c.vline(x + bw - 8 * s // 4 - ww // 2, wy, wy + ww, HOUSE)
    # chimney with a curl of smoke
    c.rect(x + bw - 14 * s // 4, y - 2 * s // 4,
           x + bw - 8 * s // 4, y + 14 * s // 4, ROOF)
    c.disc(x + bw - 11 * s // 4, y - 8 * s // 4, 3 * s // 4 + 1, PAPER_EDGE)
    c.disc(x + bw - 8 * s // 4, y - 14 * s // 4, 2 * s // 4 + 1, PAPER_EDGE)


def draw_sun(c, cx, cy, r):
    for k in range(8):
        ang = k * 3.141592653589793 / 4
        x0 = int(cx + (r + 4) * math.cos(ang))
        y0 = int(cy + (r + 4) * math.sin(ang))
        x1 = int(cx + (r + 14) * math.cos(ang))
        y1 = int(cy + (r + 14) * math.sin(ang))
        c.line(x0, y0, x1, y1, SUN, 2)
    c.disc(cx, cy, r, SUN_CORE)
    c.ring(cx, cy, r, SUN, 2)


def draw_flower(c, x, y, s, petal):
    c.vline(x, y, y + 26 * s // 4, GREEN, 2)
    c.line(x, y + 14 * s // 4, x - 8 * s // 4, y + 8 * s // 4, LEAF, 2)
    c.line(x, y + 18 * s // 4, x + 8 * s // 4, y + 12 * s // 4, LEAF, 2)
    for dx, dy in ((-7, -7), (7, -7), (-7, 7), (7, 7), (0, -10), (0, 10),
                   (-10, 0), (10, 0)):
        c.disc(x + dx * s // 4, y + dy * s // 4, 4 * s // 4, petal)
    c.disc(x, y, 4 * s // 4, SUN_CORE)


def draw_letter():
    c = Canvas(W, H)
    # warm wall, top to bottom gradient
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(WALL_TOP[i] + (WALL_BOTTOM[i] - WALL_TOP[i]) * t)
                    for i in range(3))
        c.hline(0, W - 1, y, col)
    # paper with a soft shadow
    c.rect(80, 58, 960, 984, SHADOW)
    c.rect(72, 48, 952, 976, PAPER)
    # double border
    c.rect(86, 62, 938, 962, PAPER_EDGE)
    c.rect(88, 64, 936, 960, PAPER)
    for (x0, y0, x1, y1) in ((96, 72, 928, 72), (96, 952, 928, 952)):
        c.hline(x0, x1, y0, INK_SOFT, 2)
    for (x, y0, y1) in ((96, 72, 952), (928, 72, 952)):
        c.vline(x, y0, y1, INK_SOFT, 2)

    # header illustration: sun, house, flowers
    draw_sun(c, 868, 122, 22)
    draw_house(c, 452, 92, 4)
    draw_flower(c, 150, 122, 4, RED)
    draw_flower(c, 196, 132, 3, (214, 120, 160))
    draw_flower(c, 796, 140, 3, (214, 120, 160))

    # title + subtitle
    c.text(TITLE, W // 2, 188, 6, RED, align="center")
    c.text(SUBTITLE, W // 2, 236, 3, INK_SOFT, align="center")
    # divider with a heart
    c.hline(180, 470, 272, INK_SOFT, 2)
    c.hline(554, 844, 272, INK_SOFT, 2)
    c.glyph("\u2665", 502, 260, 3, RED)

    # body
    y = 300
    scale = 4
    line_h = 36
    max_w = 804
    left = 110
    for i, para in enumerate(BODY):
        lines = c.wrap(para, scale, max_w)
        for line in lines:
            c.text(line, left, y, scale, INK)
            y += line_h
        if i == 0:
            y += 4           # a breath after the greeting
        elif i < len(BODY) - 1:
            y += 6           # paragraph spacing

    # sign-off
    y += 4
    c.text(SIGNOFF[0], left, y, scale, INK)
    y += line_h
    c.text(SIGNOFF[1], left, y, scale, INK)

    # wax seal with a heart, bottom right
    c.disc(836, y - 6, 34, RED)
    c.disc(836, y - 6, 27, RED_DARK)
    c.disc(836, y - 6, 24, RED)
    c.glyph("\u2665", 824, y - 18, 3, (255, 232, 210))

    # postscript
    c.text(POSTSCRIPT, left, 922, 3, INK_SOFT)
    return c


def main():
    canvas = draw_letter()
    data = encode_png(canvas)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    print(f"wrote {OUTPUT} ({len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
