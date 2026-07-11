#!/usr/bin/env python3
"""Build zzz-ZZZZZZZVetInsignia.big: rank insignia art for veterancy levels 5-8.

The GeneralsX feature/veterancy-8-levels engine branch extends veterancy to 8
levels (HEROIC2..HEROIC5, indices 4..7).  The engine looks up NEW MappedImage
names for the extra ranks and falls back to the HEROIC art when they are
missing, so this layer is purely additive art:

  world-space health-bar insignia (Drawable::drawVeterancy):
    SCVeter4   HEROIC2  gold star above 1 chevron        (9 x 13 px)
    SCVeter5   HEROIC3  gold star above 2 chevrons       (9 x 16 px)
    SCVeter6   HEROIC4  gold star above 3 chevrons       (9 x 19 px)
    SCVeter7   HEROIC5  double gold star above 3 chevrons(19 x 19 px)

  control-bar cameo rank overlay (ControlBar::calculateVeterancyOverlay*):
    SSChevron4L HEROIC2  large star above 1 chevron       (120 x 96 cell)
    SSChevron5L HEROIC3  large star above 2 chevrons
    SSChevron6L HEROIC4  large star above 3 chevrons
    SSChevron7L HEROIC5  large double star above 3 chevrons

Visual style: the chevrons are pixel-exact copies of the shipped rank art --
the 5px-wide yellow/orange/black SCVeter chevron stacks from the base ZH
scgameuserinterface512_001.tga (identical bytes in ShockWave's override), and
the 28px-wide antialiased gold chevrons the ShockWave stack actually renders
on the cameo (SNSUserInterface512_001.tga, which the mod's SSUserInterface512
MappedImages point SSChevron*L at).  The stars are generated procedurally in
the matching palettes: a hand-tuned 9x7 yellow/orange pixel star for the
world icons, and a supersampled 5-point star with a gold gradient
(250,224,40 -> 170,124,0) plus 1px black outline for the cameo, sampled from
the SNS chevron golds.

Ships (all NEW paths / NEW MappedImage names -- owns nothing shared):
  Art\\Textures\\ZZVetInsignia.tga                            (256x256 32-bit TGA)
  Data\\INI\\MappedImages\\HandCreated\\VeterancyInsignia.INI (8 MappedImage blocks)

HandCreated MappedImages are loaded last (ImageCollection::load), so the new
names are guaranteed visible; nothing existing is overridden.  Without this
layer (or outside the mod stack) the engine silently keeps the HEROIC art.
"""

import math
import os
import struct
import sys

sys.path.insert(0, "/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon")
from bigfile import read_big, write_big_file, BigEntry, find_entry

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "zzz-ZZZZZZZVetInsignia.big"
OUT_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
]
BASE_TEX_BIG = os.path.expanduser("~/GeneralsX/GeneralsZH/TexturesZH.big")
SHW_TEX_BIG = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/!ShwTextures.big")
SHW_ART_BIG = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/!Shw2DArt.big")

TEXTURE_NAME = "ZZVetInsignia.tga"
TEX_PATH = "Art\\Textures\\" + TEXTURE_NAME
INI_PATH = "Data\\INI\\MappedImages\\HandCreated\\VeterancyInsignia.INI"
ATLAS_W = ATLAS_H = 256
NEW_IMAGE_NAMES = ["SCVeter4", "SCVeter5", "SCVeter6", "SCVeter7",
                   "SSChevron4L", "SSChevron5L", "SSChevron6L", "SSChevron7L"]

# donor sprite locations (pixel rects, exclusive right/bottom like MappedImage Coords)
SCVETER_SRC = {1: (497, 46, 502, 51), 2: (497, 36, 502, 44), 3: (497, 23, 502, 34)}
# SNS cameo chevron sprites: cell origin + opaque bbox (28 wide, right column x89..116)
SNS_CHEV_SRC = {1: (367 + 89, 99 + 2, 367 + 117, 99 + 25),
                2: (123 + 89, 197 + 2, 123 + 117, 197 + 35),
                3: (367 + 89, 197 + 2, 367 + 117, 197 + 45)}
CELL_W, CELL_H = 120, 96   # SSChevron*L cell size (must match the 1L..3L donors)


# ---------------------------------------------------------------- TGA helpers
def read_tga(data):
    idlen, cmap, imgtype = data[0], data[1], data[2]
    assert imgtype == 2 and cmap == 0, f"unsupported TGA type {imgtype}"
    w, h = struct.unpack("<HH", data[12:16])
    bpp, desc = data[16], data[17]
    assert bpp == 32, f"expected 32-bit TGA, got {bpp}"
    n = 4
    off = 18 + idlen
    raw = data[off:off + w * h * n]
    top_down = bool(desc & 0x20)
    px = [[None] * w for _ in range(h)]
    for row in range(h):
        y = row if top_down else (h - 1 - row)
        base = row * w * n
        for x in range(w):
            i = base + x * n
            px[y][x] = (raw[i + 2], raw[i + 1], raw[i], raw[i + 3])  # RGBA
    return px, w, h


def write_tga_bytes(px, w, h):
    """32-bit uncompressed, bottom-up rows, desc=0x08 (matches shipped assets)."""
    hdr = bytes(12) + struct.pack("<HH", w, h) + bytes([32, 0x08])
    hdr = bytes([0, 0, 2]) + hdr[3:]
    body = bytearray()
    for row in range(h):
        y = h - 1 - row
        for x in range(w):
            r, g, b, a = px[y][x]
            body += bytes((b, g, r, a))
    return hdr + bytes(body)


def crop(px, l, t, r, b):
    """Exclusive right/bottom, like MappedImage Coords."""
    return [row[l:r] for row in px[t:b]], (r - l), (b - t)


def blank(w, h, fill=(0, 0, 0, 0)):
    return [[fill] * w for _ in range(h)]


def blit(dst, src, sw, sh, dx, dy):
    for y in range(sh):
        for x in range(sw):
            p = src[y][x]
            if p[3] > 0:
                dst[dy + y][dx + x] = p


def write_png(path, px, w, h, scale=1):
    import zlib
    raw = bytearray()
    for y in range(h):
        rowbytes = bytearray()
        for x in range(w):
            rowbytes += bytes(px[y][x]) * scale
        for _ in range(scale):
            raw.append(0)
            raw += rowbytes

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w * scale, h * scale, 8, 6, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- star art
def star_coverage(size, ss=5, inner=0.47):
    """Coverage grid (0..1) of a point-up 5-point star filling size x size."""
    pts = []
    cx = cy = (size - 1) / 2.0
    R = size / 2.0
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = R if i % 2 == 0 else R * inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    def inside(x, y):
        c = False
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            if (y1 > y) != (y2 > y):
                if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                    c = not c
        return c

    cov = [[0.0] * size for _ in range(size)]
    for py in range(size):
        for px_ in range(size):
            hits = sum(1 for sy in range(ss) for sx in range(ss)
                       if inside(px_ + (sx + 0.5) / ss, py + (sy + 0.5) / ss))
            cov[py][px_] = hits / (ss * ss)
    return cov


def render_big_star(size=25, fill_top=(250, 224, 40), fill_bot=(170, 124, 0)):
    """Antialiased gradient star with 1px black outline (SNS cameo style)."""
    cov = star_coverage(size)
    out = blank(size + 2, size + 2)
    for y in range(size):
        t = y / (size - 1)
        col = tuple(int(round(fill_top[i] + (fill_bot[i] - fill_top[i]) * t)) for i in range(3))
        for x in range(size):
            if cov[y][x] >= 0.5:
                out[y + 1][x + 1] = (col[0], col[1], col[2], 255)
            elif cov[y][x] > 0.15:
                out[y + 1][x + 1] = (col[0], col[1], col[2], int(255 * cov[y][x]))
    W = H = size + 2
    res = [row[:] for row in out]
    for y in range(H):
        for x in range(W):
            if out[y][x][3] == 0:
                if any(out[y + dy][x + dx][3] > 128
                       for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                       if 0 <= y + dy < H and 0 <= x + dx < W):
                    res[y][x] = (0, 0, 0, 255)
    return res, W, H


def tiny_star():
    """Hand-tuned 9x7 pixel star in the SCVeter chevron palette."""
    Y = (0xF9, 0xF4, 0x00, 255)   # bright yellow (chevron edge)
    O = (0xEE, 0x89, 0x00, 255)   # orange (chevron core)
    m = {"Y": Y, "O": O, ".": (0, 0, 0, 0)}
    grid = [
        "....Y....",
        "...YYY...",
        "YYYYOYYYY",
        ".YYOOOYY.",
        "..YOOOY..",
        "..YOYOY..",
        ".YY...YY.",
    ]
    return [[m[c] for c in row] for row in grid], 9, 7


# ---------------------------------------------------------------- build
def compose_sprites(base_px, sns_px):
    """Return {image_name: (pixels, w, h)} for the 8 new insignia."""
    sprites = {}

    # world-space SCVeter4..7
    chev = {n: crop(base_px, *SCVETER_SRC[n]) for n in (1, 2, 3)}
    star, sw, sh = tiny_star()
    for n in (1, 2, 3):
        c, cw, ch = chev[n]
        w, h = 9, sh + 1 + ch
        cv = blank(w, h)
        blit(cv, star, sw, sh, 0, 0)
        blit(cv, c, cw, ch, 2, sh + 1)          # chevrons centered under the star
        sprites[f"SCVeter{3 + n}"] = (cv, w, h)
    c, cw, ch = chev[3]
    w, h = 19, sh + 1 + ch
    cv = blank(w, h)
    blit(cv, star, sw, sh, 0, 0)
    blit(cv, star, sw, sh, 10, 0)
    blit(cv, c, cw, ch, 7, sh + 1)
    sprites["SCVeter7"] = (cv, w, h)

    # cameo SSChevron4L..7L (120x96 cells, right-aligned column like the donors)
    big = {n: crop(sns_px, *SNS_CHEV_SRC[n]) for n in (1, 2, 3)}
    bstar, bw, bh = render_big_star()
    for n in (1, 2, 3):
        c, cw, ch = big[n]
        cell = blank(CELL_W, CELL_H)
        blit(cell, bstar, bw, bh, 89 + (28 - bw) // 2, 2)
        blit(cell, c, cw, ch, 89, 2 + bh + 2)
        sprites[f"SSChevron{3 + n}L"] = (cell, CELL_W, CELL_H)
    c, cw, ch = big[3]
    cell = blank(CELL_W, CELL_H)
    x2 = 117 - bw                                # right star flush with column right edge
    blit(cell, bstar, bw, bh, x2 - bw - 1, 2)
    blit(cell, bstar, bw, bh, x2, 2)
    blit(cell, c, cw, ch, 89, 2 + bh + 2)
    sprites["SSChevron7L"] = (cell, CELL_W, CELL_H)
    return sprites


def pack_atlas(sprites):
    """Place sprites on the 256x256 atlas; return (atlas_px, {name: rect})."""
    atlas = blank(ATLAS_W, ATLAS_H)
    coords = {}
    slots = {  # fixed layout: 4 cameo cells + world strip, 2px padding everywhere
        "SSChevron4L": (2, 2), "SSChevron5L": (126, 2),
        "SSChevron6L": (2, 102), "SSChevron7L": (126, 102),
        "SCVeter4": (2, 202), "SCVeter5": (15, 202),
        "SCVeter6": (28, 202), "SCVeter7": (41, 202),
    }
    for name, (x, y) in slots.items():
        px, w, h = sprites[name]
        assert x + w <= ATLAS_W and y + h <= ATLAS_H, name
        blit(atlas, px, w, h, x, y)
        coords[name] = (x, y, x + w, y + h)
    # no-overlap check
    rects = list(coords.values())
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1], \
                f"atlas overlap {a} {b}"
    return atlas, coords


def mapped_images_ini(coords):
    lines = ["; zzz-ZZZZZZZVetInsignia: rank insignia for extended veterancy levels",
             "; HEROIC2..HEROIC5 (GeneralsX feature/veterancy-8-levels engine branch).",
             "; SCVeter4..7 = world-space health-bar icons, SSChevron4L..7L = cameo overlay.",
             ""]
    for name in NEW_IMAGE_NAMES:
        l, t, r, b = coords[name]
        lines += [f"MappedImage {name}",
                  f"  Texture = {TEXTURE_NAME}",
                  f"  TextureWidth = {ATLAS_W}",
                  f"  TextureHeight = {ATLAS_H}",
                  f"  Coords = Left:{l} Top:{t} Right:{r} Bottom:{b}",
                  "  Status = NONE",
                  "End", ""]
    return "\r\n".join(lines)


def main():
    # ---- donors ----
    base_tex = read_big(BASE_TEX_BIG)
    base_entry = find_entry(base_tex, "Art\\Textures\\scgameuserinterface512_001.tga")
    base_px, _, _ = read_tga(base_entry.data)

    # ShockWave overrides this atlas; assert the SCVeter region is identical so the
    # world-icon style is right in the mod stack too.
    shw_tex = read_big(SHW_TEX_BIG)
    shw_entry = find_entry(shw_tex, "Art\\Textures\\scgameuserinterface512_001.tga")
    shw_px, _, _ = read_tga(shw_entry.data)
    for l, t, r, b in SCVETER_SRC.values():
        for y in range(t, b):
            for x in range(l, r):
                assert base_px[y][x] == shw_px[y][x], "SCVeter donor art drifted in ShockWave"

    shw_art = read_big(SHW_ART_BIG)
    sns_entry = find_entry(shw_art, "Art\\Textures\\SNSUserInterface512_001.tga")
    sns_px, _, _ = read_tga(sns_entry.data)
    # sanity: donor cameo chevrons are where we think (opaque content in each rect)
    for n, (l, t, r, b) in SNS_CHEV_SRC.items():
        assert any(sns_px[y][x][3] > 0 for y in range(t, b) for x in range(l, r)), n

    # ---- compose ----
    sprites = compose_sprites(base_px, sns_px)
    atlas, coords = pack_atlas(sprites)
    tga_bytes = write_tga_bytes(atlas, ATLAS_W, ATLAS_H)
    ini_text = mapped_images_ini(coords)

    # round-trip the TGA we just wrote
    rt_px, rt_w, rt_h = read_tga(tga_bytes)
    assert (rt_w, rt_h) == (ATLAS_W, ATLAS_H) and rt_px == atlas, "TGA round-trip failed"

    # ---- ownership / collision checks across the installed stacks ----
    for d in OUT_DIRS:
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(".big") or f == OUT_NAME:
                continue
            for e in read_big(os.path.join(d, f)):
                pl = e.path.lower()
                assert pl != TEX_PATH.lower() and pl != INI_PATH.lower(), \
                    f"path owned by {f}: {e.path}"
                if "mappedimages" in pl and pl.endswith((".ini",)):
                    text = e.data.decode("latin-1", "replace").lower()
                    for name in NEW_IMAGE_NAMES:
                        assert f"mappedimage {name.lower()}" not in text, \
                            f"image name {name} already defined in {f}:{e.path}"

    # ---- package & install ----
    out_entries = [BigEntry(TEX_PATH, tga_bytes),
                   BigEntry(INI_PATH, ini_text.encode("latin-1"))]
    out_entries.sort(key=lambda e: e.path.lower())
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(out_entries, out_local)
    local_bytes = open(out_local, "rb").read()
    for d in OUT_DIRS:
        with open(os.path.join(d, OUT_NAME), "wb") as fo:
            fo.write(local_bytes)

    # ---- verify installed archives round-trip ----
    for d in OUT_DIRS:
        p = os.path.join(d, OUT_NAME)
        assert open(p, "rb").read() == local_bytes, f"install mismatch: {p}"
        back = read_big(p)
        assert {e.path: e.data for e in back} == {e.path: e.data for e in out_entries}, p

    # sort-order sanity: our zzz- name must not shadow anything it shouldn't (all new
    # paths, so priority is irrelevant; just confirm the file lands in the listing)
    for d in OUT_DIRS:
        bigs = sorted(f.lower() for f in os.listdir(d) if f.lower().endswith(".big"))
        assert OUT_NAME.lower() in bigs, d

    # ---- previews (documentation) ----
    pv = os.path.join(HERE, "preview")
    os.makedirs(pv, exist_ok=True)
    write_png(os.path.join(pv, "atlas.png"), atlas, ATLAS_W, ATLAS_H, scale=1)
    strip = blank(130, 24, (40, 40, 40, 255))
    x = 2
    for n in (1, 2, 3):
        c, cw, ch = crop(base_px, *SCVETER_SRC[n])
        blit(strip, c, cw, ch, x, 2)
        x += cw + 6
    for lvl in (4, 5, 6, 7):
        cv, w, h = sprites[f"SCVeter{lvl}"]
        blit(strip, cv, w, h, x, 2)
        x += w + 6
    write_png(os.path.join(pv, "world_ranks_1_to_7.png"), strip, 130, 24, scale=8)
    for lvl in (4, 5, 6, 7):
        cell, w, h = sprites[f"SSChevron{lvl}L"]
        write_png(os.path.join(pv, f"cameo_SSChevron{lvl}L.png"), cell, w, h, scale=2)

    # ---- report ----
    print("SPRITES:")
    for name in NEW_IMAGE_NAMES:
        px, w, h = sprites[name]
        l, t, r, b = coords[name]
        print(f"  {name:12s} {w:3d}x{h:<3d} at atlas ({l},{t})-({r},{b})")
    print("\nFILES IN ARCHIVE (%d):" % len(out_entries))
    for e in out_entries:
        print(f"  {len(e.data):>9}  {e.path}")
    print("\nINSTALLED:")
    for d in OUT_DIRS:
        print("  ", os.path.join(d, OUT_NAME))
    print("\nALL VERIFICATIONS PASSED")


if __name__ == "__main__":
    main()
