#!/usr/bin/env python3
"""Resolve every art asset the ported blocks need:
  - classify each token: base (vanilla/ShockWave/mod-dir archives) vs fetch-from-ROTR
  - detect filename collisions (same basename already present in the effective
    space or vanilla archives -> must ship under a renamed file)
  - fetch needed files from the ROTR gibs (ranged), then parse the fetched
    W3D binaries for internal texture references and resolve those too.
Writes work/art_manifest.json for build.py.
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "hotkey-addon"))
from bigfile import read_big  # noqa: E402
from rotrfetch import RotrArt  # noqa: E402

VANILLA = os.path.expanduser("~/GeneralsX/GeneralsZH")
SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")

# ---- basenames available in the base game + effective mod space ------------
def base_art_index():
    cache = os.path.join(HERE, "base_art_index.json")
    if os.path.exists(cache):
        return json.load(open(cache))
    idx = {}   # lower basename -> "archive:path"
    for d, bigs in (
            (os.path.join(VANILLA, "ZH_Generals"), ["W3D.big", "Textures.big", "Patch.big"]),
            (VANILLA, ["W3DZH.big", "TexturesZH.big", "PatchZH.big"])):
        for b in bigs:
            fp = os.path.join(d, b)
            if not os.path.exists(fp):
                continue
            for e in read_big(fp):
                idx.setdefault(e.path.rsplit("\\", 1)[-1].lower(), "%s:%s" % (b, e.path))
    # every archive in the SPE mod dir (later wins, but presence is presence)
    for b in sorted(os.listdir(SPE), key=str.lower):
        if not b.lower().endswith(".big"):
            continue
        if b.lower() == "zzz-zzzzzzzrotrinfantry.big":
            continue
        for e in read_big(os.path.join(SPE, b)):
            idx["%s" % e.path.rsplit("\\", 1)[-1].lower()] = "%s:%s" % (b, e.path)
    json.dump(idx, open(cache, "w"))
    return idx


# W3D binary: walk chunks, collect W3D_CHUNK_TEXTURE_NAME (0x00000032) strings
def w3d_texture_names(fp):
    names = set()
    data = open(fp, "rb").read()

    def walk(buf, start, end):
        pos = start
        while pos + 8 <= end:
            (ctype,) = struct.unpack_from("<I", buf, pos)
            (csize,) = struct.unpack_from("<I", buf, pos + 4)
            has_sub = bool(csize & 0x80000000)
            csize &= 0x7FFFFFFF
            body = pos + 8
            if body + csize > end:
                break
            if ctype == 0x00000032:  # TEXTURE_NAME
                s = buf[body:body + csize].split(b"\x00")[0].decode("latin-1")
                if s:
                    names.add(s)
            elif has_sub or ctype in (0x0, 0x1F, 0x28, 0x29, 0x2A, 0x2B, 0x30, 0x31, 0x38):
                walk(buf, body, body + csize)
            pos = body + csize
    walk(data, 0, len(data))
    return names


def main():
    needed = json.load(open(os.path.join(HERE, "art_needed.json")))
    models = needed["models"]          # w3d basenames without extension
    textures = needed["textures"]      # texture basenames without extension
    base = base_art_index()
    rotr = RotrArt()

    manifest = {"ship": [],            # (internal path, local file)
                "base": [],            # resolved by base game / effective space
                "collide_rename": {},  # old basename -> new basename
                "missing": []}

    def texture_candidates(tok):
        return [tok + ".dds", tok + ".tga"]

    def resolve_texture(tok, force_ship=False):
        tok_l = tok.lower()
        in_base = [c for c in texture_candidates(tok_l) if c in base]
        if in_base and not force_ship:
            manifest["base"].append((tok, base[in_base[0]]))
            return
        hit = None
        for cand in texture_candidates(tok):
            hit = rotr.find(cand)
            if hit:
                break
        if not hit:
            manifest["missing"].append(("texture", tok))
            return
        path, local = rotr.fetch(hit[1])
        if in_base:   # same basename exists in base with (assumed) different content
            manifest["collide_rename"][path.rsplit("\\", 1)[-1]] = None  # build decides
        manifest["ship"].append((path, local))

    fetched_w3d = []
    for tok in sorted(set(models)):
        f = tok.lower() + ".w3d"
        if f in base:
            manifest["base"].append((tok, base[f]))
            continue
        hit = rotr.find(tok + ".w3d")
        if not hit:
            manifest["missing"].append(("w3d", tok))
            continue
        path, local = rotr.fetch(hit[1])
        manifest["ship"].append((path, local))
        fetched_w3d.append(local)

    # texture closure of fetched W3Ds
    tex_all = set(t.lower() for t in textures)
    for local in fetched_w3d:
        for t in w3d_texture_names(local):
            tex_all.add(t.rsplit(".", 1)[0].lower())

    for tok in sorted(tex_all):
        resolve_texture(tok)

    json.dump(manifest, open(os.path.join(HERE, "art_manifest.json"), "w"), indent=1)
    print("ship=%d base=%d missing=%d collide=%d" % (
        len(manifest["ship"]), len(manifest["base"]), len(manifest["missing"]),
        len(manifest["collide_rename"])))
    for kind, tok in manifest["missing"]:
        print("  MISSING", kind, tok)
    for k in manifest["collide_rename"]:
        print("  COLLIDES with base:", k)


if __name__ == "__main__":
    main()
