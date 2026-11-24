#!/usr/bin/env python3
"""Draw one image summing up Monday 23 November 2026's world news.

A newspaper front page, drawn entirely in code with the Python standard
library only: a tiny 5x7 bitmap font, filled shapes, and a small PNG
writer (zlib + struct). No network, no clock, no randomness, so two runs
write identical bytes.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes $MAKEFUN_OUTPUT_DIR/entry.png (default: out/entry.png).
"""
import os
import struct
import zlib

W, H = 1024, 1024
INK = (20, 20, 20)
PAPER = (250, 247, 238)
RED = (178, 34, 28)
GREY = (110, 108, 100)
LIGHT = (232, 228, 218)
BLUE = (28, 68, 128)
TEAL = (18, 110, 105)
ORANGE = (214, 110, 20)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, written out by hand. '#' is a set pixel.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
}

# ---------------------------------------------------------------- canvas
buf = bytearray(PAPER[0] for _ in range(W * H * 3))
for _i in range(W * H):
    buf[_i * 3:_i * 3 + 3] = bytes(PAPER)


def put(x, y, col):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o:o + 3] = bytes(col)


def rect(x, y, w, h, col):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(xx, yy, col)


def hline(x0, x1, y, col):
    for xx in range(min(x0, x1), max(x0, x1) + 1):
        put(xx, y, col)


def vline(x, y0, y1, col):
    for yy in range(min(y0, y1), max(y0, y1) + 1):
        put(x, yy, col)


def line(x0, y0, x1, y1, col):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        put(x0, y0, col)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, col, fill=False):
    if fill:
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                put(xx, yy, col)
    else:
        steps = max(8, r * 8)
        import math
        for i in range(steps):
            a = 2 * math.pi * i / steps
            put(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), col)


def poly(points, col):
    """Fill a polygon with a scanline fill."""
    if not points:
        return
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[j]), int(xs[j + 1]) + 1):
                put(xx, y, col)


def burst(cx, cy, r1, r2, col):
    """A starburst: alternating long/short spikes."""
    import math
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
    poly(pts, col)

# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, col):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for row in range(7):
            for c in range(5):
                if g[row][c] == '#':
                    rect(cx + c * scale, y + row * scale, scale, scale, col)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, col):
    draw_text((W - text_w(s, scale)) // 2, y, s, scale, col)


def wrap(s, max_chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, col, max_chars, lh=None):
    lh = lh or (7 * scale + 4)
    for ln in wrap(s, max_chars):
        draw_text(x, y, ln, scale, col)
        y += lh
    return y

# ---------------------------------------------------------------- icons
def icon_ship(x, y, w, h):
    """Warship at sea with an explosion above it."""
    cx, cy = x + w // 2, y + h // 2
    burst(cx + 55, cy - 42, 26, 12, ORANGE)
    burst(cx + 55, cy - 42, 14, 7, RED)
    # hull
    poly([(cx - 95, cy + 8), (cx + 95, cy + 8), (cx + 70, cy + 38),
          (cx - 70, cy + 38)], BLUE)
    rect(cx - 95, cy + 8, 190, 6, INK)
    # deck house + mast + funnel
    rect(cx - 55, cy - 18, 70, 26, INK)
    rect(cx + 18, cy - 30, 16, 38, GREY)
    vline(cx - 30, cy - 48, cy - 18, INK)
    poly([(cx - 30, cy - 48), (cx - 2, cy - 40), (cx - 30, cy - 32)], RED)
    # waves
    for k, wy in enumerate((cy + 52, cy + 66)):
        for xx in range(x + 10 + k * 20, x + w - 10, 44):
            line(xx, wy, xx + 12, wy - 8, TEAL)
            line(xx + 12, wy - 8, xx + 24, wy, TEAL)


def icon_globe(x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    circle(cx, cy, 21, TEAL, fill=True)
    circle(cx, cy, 21, INK)
    for dy in (-10, 0, 10):
        hline(cx - 19, cx + 19, cy + dy, PAPER)
    vline(cx, cy - 21, cy + 21, PAPER)
    # red cross over the deal: no agreement
    line(cx + 24, cy - 16, cx + 44, cy + 4, RED)
    line(cx + 44, cy - 16, cx + 24, cy + 4, RED)


def icon_building(x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    # leaning, cracked apartment block
    poly([(cx - 22, cy - 24), (cx + 18, cy - 24), (cx + 22, cy + 22),
          (cx - 18, cy + 22)], GREY)
    for r in range(3):
        for c in range(2):
            rect(cx - 15 + c * 16, cy - 18 + r * 13, 9, 7, (255, 235, 130))
    line(cx - 6, cy - 24, cx + 4, cy - 4, INK)
    line(cx + 4, cy - 4, cx - 5, cy + 14, INK)
    # fallen rubble
    poly([(cx + 20, cy + 14), (cx + 38, cy + 20), (cx + 30, cy + 24),
          (cx + 18, cy + 22)], INK)
    burst(cx - 28, cy - 16, 11, 6, ORANGE)


def icon_barrel(x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    # oil barrel with a blockade cross over it
    rect(cx - 16, cy - 20, 32, 40, INK)
    rect(cx - 19, cy - 14, 38, 4, ORANGE)
    rect(cx - 19, cy + 6, 38, 4, ORANGE)
    line(cx - 30, cy - 24, cx + 30, cy + 24, RED)
    line(cx + 30, cy - 24, cx - 30, cy + 24, RED)


def icon_chip(x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    rect(cx - 18, cy - 18, 36, 36, TEAL)
    rect(cx - 10, cy - 10, 20, 20, PAPER)
    rect(cx - 4, cy - 4, 8, 8, RED)
    for k in range(3):
        vline(cx - 12 + k * 12, cy - 25, cy - 18, INK)
        vline(cx - 12 + k * 12, cy + 18, cy + 25, INK)
        hline(cx - 25, cx - 18, cy - 12 + k * 12, INK)
        hline(cx + 18, cx + 25, cy - 12 + k * 12, INK)
    # rising arrow
    line(cx + 24, cy + 18, cx + 44, cy - 2, RED)
    line(cx + 44, cy - 2, cx + 34, cy - 2, RED)
    line(cx + 44, cy - 2, cx + 44, cy + 8, RED)


def icon_flame(x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    poly([(cx - 20, cy + 20), (cx - 22, cy - 4), (cx - 10, cy - 16),
          (cx - 4, cy - 24), (cx + 6, cy - 10), (cx + 20, cy - 18),
          (cx + 22, cy + 4), (cx + 14, cy + 20)], ORANGE)
    poly([(cx - 9, cy + 18), (cx - 8, cy + 2), (cx, cy - 10),
          (cx + 8, cy + 2), (cx + 9, cy + 18)], RED)
    rect(cx - 26, cy + 20, 52, 4, INK)

# ---------------------------------------------------------------- layout
def panel(x, y, w, h, kicker, headline, body, icon=None):
    rect(x, y, w, h, (255, 255, 255))
    for xx in range(x, x + w):
        put(xx, y, INK)
        put(xx, y + h - 1, INK)
    for yy in range(y, y + h):
        put(x, yy, INK)
        put(x + w - 1, yy, INK)
    tx = x + 16
    ty = y + 12
    if icon is not None:
        rect(x + 1, y + 1, w - 2, 52, LIGHT)
        icon(x, y + 1, w, 52)
        ty = y + 64
    draw_text(tx, ty, kicker, 2, RED)
    ty += 20
    ty = para(tx, ty, headline, 3, INK, (w - 32) // 18, lh=23)
    para(tx, ty + 2, body, 2, INK, (w - 32) // 12, lh=17)


def build():
    # frame
    rect(0, 0, W, 12, INK)
    rect(0, H - 12, W, 12, INK)
    rect(0, 0, 12, H, INK)
    rect(W - 12, 0, 12, H, INK)

    # masthead
    draw_centered(34, "THE WORLD IN ONE DAY", 6, INK)
    hline(24, W - 25, 96, INK)
    hline(24, W - 25, 100, INK)
    draw_centered(110, "ONE DAY - ONE PAGE - THE WHOLE WORLD", 2, GREY)

    # red date bar
    rect(24, 136, W - 48, 44, RED)
    draw_centered(149, "MONDAY, 23 NOVEMBER 2026 - WORLD NEWS", 3, (255, 255, 255))

    # lead story
    lx, ly, lw, lh = 24, 194, W - 48, 196
    rect(lx, ly, lw, lh, (255, 255, 255))
    for xx in range(lx, lx + lw):
        put(xx, ly, INK)
        put(xx, ly + lh - 1, INK)
    for yy in range(ly, ly + lh):
        put(lx, yy, INK)
        put(lx + lw - 1, yy, INK)
    draw_text(lx + 18, ly + 14, "LEAD STORY - BENGHAZI, LIBYA", 2, RED)
    para(lx + 18, ly + 42, "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
         3, INK, 32, lh=25)
    para(lx + 18, ly + 100,
         "Seven naval drones sank the Russian corvette Merkury at "
         "Benghazi, President Zelensky said on Monday, in a strike "
         "1,500 miles from the front line. A cargo ship was hit too.",
         2, INK, 48, lh=18)
    icon_ship(lx + 640, ly + 8, 330, 180)

    # grid: three panels, then two wider panels
    panel(24, 406, 312, 216, "CLIMATE - ANTALYA",
          "COP31 ENDS WITH NO DEAL",
          "The longest climate summit ended with no deal, the "
          "first collapse in 17 years.",
          icon_globe)
    panel(356, 406, 312, 216, "UKRAINE - DYMER",
          "STRIKE KILLS 11 IN DYMER",
          "A drone collapsed a block north of Kyiv. A boy aged "
          "seven was pulled alive from the rubble.",
          icon_building)
    panel(688, 406, 312, 216, "IRAN - HORMUZ",
          "TEHRAN VOWS TO FIGHT BLOCKADE",
          "Iran vowed to use every means against the US naval "
          "blockade of Hormuz.",
          icon_barrel)
    panel(24, 638, 480, 216, "MARKETS - NVIDIA",
          "HUANG BACK AT NVIDIA AS SHARES SOAR",
          "Nvidia reinstated Jensen Huang as chief executive, "
          "11 days after he resigned, and shares jumped about "
          "31% after US government input.",
          icon_chip)
    panel(520, 638, 480, 216, "INDONESIA - CIKANDE",
          "FACTORY FIRE KILLS 24, DOZENS MISSING",
          "A blaze tore through a sweets factory in Cikande, "
          "Banten. At least 24 people were confirmed dead and "
          "about 30 were still missing on Monday.",
          icon_flame)

    # ticker
    rect(24, 870, W - 48, 62, INK)
    para(40, 880,
         "SUDAN: DRONES HIT A UN BUILDING IN KHARTOUM - EU PROPOSES "
         "NEW RUSSIA SANCTIONS - S. KOREA MINISTER QUITS - "
         "BEPICOLOMBO REACHES MERCURY",
         2, (255, 255, 255), 78, lh=18)

    # footer
    draw_centered(948, "DRAWN IN CODE - NO PHOTOGRAPHS", 2, GREY)


# ---------------------------------------------------------------- png
def write_png(path):
    raw = b""
    for y in range(H):
        raw += b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    build()
    path = os.path.join(outdir, "entry.png")
    n = write_png(path)
    print(f"wrote {path} ({n} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
