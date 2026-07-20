#!/usr/bin/env python3
"""Transplant the canonical SW 16-side skirmish configuration into community maps.

Engine facts driving this tool (GeneralsX vet8 sources):
  * SidesList::prepareForMP_or_Skirmish (SidesList.cpp:479): if ANY non-civilian
    embedded side has a non-empty ScriptList, SkirmishScripts.scb is NOT loaded
    at all (map scripts shadow the whole scb).  Otherwise the scb's ScriptLists
    attach to embedded sides BY playerName; scb lists with no matching side are
    deleted -> those AI generals idle.
  * Player.cpp:~890 (initFromDict): each lobby AI copies the skirmish side's
    ScriptList whose playerFaction template side matches its own; no match ->
    scriptless (forceHuman).
  * ParseSidesDataChunk breaks (mid-stream!) past MAX_PLAYER_COUNT=16 sides ->
    HARD CAP 16.  SW's own maps fit 16 = neutral + 15 skirmish by omitting
    PlyrCivilian; community maps carry civilian content we must preserve, so a
    14-side map can only take +2 of SW's 3 extra generals (REF order,
    SkirmishAmericaArmorGeneral omitted -- documented).

Operations per map (all on the decompressed CkMp buffer, fail-closed):
  1. EMPTY any non-civilian side's non-empty ScriptList (un-shadows the scb;
     only 4vs4 Massacre needs this -- it embeds a full stale skirmish AI).
  2. APPEND missing skirmish sides (cloned dict shape from the map's own
     SkirmishGLA side) + default teamSkirmishX team dicts + empty ScriptList
     chunks (positional side<->list alignment preserved), up to the 16 cap.
No symbol-table changes are needed (side/team values are strings, not symbols).
"""
import os, sys, struct, hashlib, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mapscript
from mapscript import rd_ascii, read_dict

MAX_SIDES = 16
# REF order (Armored Fury [SHW]): the 15 canonical skirmish sides
REF_SIDES = ["SkirmishAmerica", "SkirmishChina", "SkirmishGLA",
             "SkirmishAmericaAirForceGeneral", "SkirmishAmericaLaserGeneral",
             "SkirmishAmericaSuperWeaponGeneral", "SkirmishChinaTankGeneral",
             "SkirmishChinaNukeGeneral", "SkirmishChinaInfantryGeneral",
             "SkirmishGLADemolitionGeneral", "SkirmishGLAToxinGeneral",
             "SkirmishGLAStealthGeneral", "SkirmishChinaSpecialWeaponsGeneral",
             "SkirmishGLASalvageGeneral", "SkirmishAmericaArmorGeneral"]
FACTION = {n: "Faction" + n[len("Skirmish"):] for n in REF_SIDES}

def enc_ascii(t):
    b = t.encode("latin-1"); return struct.pack("<H", len(b)) + b

def enc_dict(pairs):
    out = bytearray(struct.pack("<H", len(pairs)))
    for keyid, typ, v in pairs:
        out += struct.pack("<I", (keyid << 8) | typ)
        if typ == 0:   out += struct.pack("<B", 1 if v else 0)
        elif typ == 1: out += struct.pack("<i", v)
        elif typ == 2: out += struct.pack("<f", v)
        elif typ == 3: out += enc_ascii(v)
        elif typ == 4:
            b = v.encode("utf-16-le"); out += struct.pack("<H", len(b)//2) + b
        else: raise ValueError(typ)
    return bytes(out)

def fix_map(src, dst, verbose=True):
    info = mapscript.analyze(src)
    buf, id2name, name2id = info["buf"], info["id2name"], info["name2id"]
    sl, psl, lists = info["sl"], info["psl"], info["lists"]
    names = [s.get("playerName") for s in info["sides"]]
    factions = [s.get("playerFaction") for s in info["sides"]]
    assert len(names) == len(lists), "side/list count mismatch"

    # ---- plan: which lists shadow the scb (non-civilian, non-empty) ----
    shadowers = []
    for i, l in enumerate(lists):
        if factions[i] == "FactionCivilian":
            continue
        sink = dict(scripts=[], contents=[], groups=[])
        mapscript.walk_tree(buf, id2name, l["ds"], l["de"], sink)
        if sink["scripts"]:
            shadowers.append((i, names[i], len(sink["scripts"])))

    # ---- plan: which sides to add ----
    missing = [n for n in REF_SIDES if n not in names]
    room = MAX_SIDES - len(names)
    adds = missing[:max(0, room)]
    omitted = missing[len(adds):]

    if not shadowers and not adds:
        return dict(src=src, changed=False, adds=[], omitted=omitted, shadowers=[])

    # ---- raw side walk (offsets) ----
    p = sl["ds"]
    (nsides,) = struct.unpack_from("<i", buf, p); p += 4
    donor_pairs = None
    for i in range(nsides):
        pairs, p = read_dict(buf, p)
        (nb,) = struct.unpack_from("<i", buf, p); p += 4
        assert nb == 0, "buildlists unsupported"
        d = {id2name.get(k): v for (k, _t, v) in pairs}
        if d.get("playerName") == "SkirmishGLA":
            donor_pairs = pairs
    sides_end = p
    assert donor_pairs is not None, "no SkirmishGLA donor side"
    # team donor: teamSkirmishGLA dict pair-shape
    team_donor = None
    for (_a, _b, d) in info["teams"]:
        if d.get("teamName") == "teamSkirmishGLA":
            team_donor = d
    assert team_donor is not None

    # ---- build appended side + team + list bytes ----
    side_bytes = b""
    for n in adds:
        pr = []
        for (k, t, v) in donor_pairs:
            nm = id2name.get(k)
            if nm in ("playerName", "playerDisplayName"): v = n
            elif nm == "playerFaction": v = FACTION[n]
            elif nm in ("playerAllies", "playerEnemies"): v = ""
            pr.append((k, t, v))
        side_bytes += enc_dict(pr) + struct.pack("<i", 0)
    team_bytes = b""
    for n in adds:
        team_bytes += enc_dict([(name2id["teamName"], 3, "team" + n),
                                (name2id["teamOwner"], 3, n),
                                (name2id["teamIsSingleton"], 0, 1)])
    empty_list = struct.pack("<IHi", name2id["ScriptList"], 1, 0)

    # ---- rebuild PlayerScriptsList: empty shadowers, append new lists ----
    shadow_idx = {i for (i, _n, _c) in shadowers}
    psl_data = b""
    for i, l in enumerate(lists):
        if i in shadow_idx:
            psl_data += struct.pack("<IHi", name2id["ScriptList"], l["ver"], 0)
        else:
            psl_data += bytes(buf[l["hp"]:l["de"]])
    psl_data += empty_list * len(adds)

    # ---- rebuild SidesList ----
    (nteams_,) = struct.unpack_from("<i", buf, info["teams_cnt_off"])
    new_sl_data = (
        struct.pack("<i", nsides + len(adds)) +
        bytes(buf[sl["ds"] + 4:sides_end]) + side_bytes +
        struct.pack("<i", nteams_ + len(adds)) +
        bytes(buf[info["teams_cnt_off"] + 4:psl["hp"]]) + team_bytes +
        struct.pack("<IHi", name2id["PlayerScriptsList"], psl["ver"], len(psl_data)) +
        psl_data)
    out = (bytes(buf[:sl["hp"]]) +
           struct.pack("<IHi", name2id["SidesList"], sl["ver"], len(new_sl_data)) +
           new_sl_data + bytes(buf[sl["de"]:]))

    # ================= VERIFY =================
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as fh:
        fh.write(out)
    info2 = mapscript.analyze(dst)
    names2 = [s.get("playerName") for s in info2["sides"]]
    assert names2 == names + adds and len(names2) <= MAX_SIDES
    assert len(info2["lists"]) == len(names2)
    # untouched top-level chunks byte-identical
    for a, b in zip(info["top"], info2["top"]):
        assert a["nm"] == b["nm"]
        if a["nm"] != "SidesList":
            assert bytes(info["buf"][a["ds"]:a["de"]]) == bytes(info2["buf"][b["ds"]:b["de"]]), a["nm"]
    # original sides preserved; new sides correct
    assert info2["sides"][:len(names)] == info["sides"]
    for i, n in enumerate(adds):
        s2 = info2["sides"][len(names) + i]
        assert s2["playerName"] == n and s2["playerFaction"] == FACTION[n]
        assert s2.get("playerIsHuman") == 0
    # teams: originals byte-identical + new default teams
    t2 = info2["teams"]
    assert len(t2) == len(info["teams"]) + len(adds)
    for (a0, a1, da), (_b0, _b1, db) in zip(info["teams"], t2):
        assert da == db
    for i, n in enumerate(adds):
        d = t2[len(info["teams"]) + i][2]
        assert d["teamName"] == "team" + n and d["teamOwner"] == n and d["teamIsSingleton"] == 1
    # script lists: non-shadowed originals byte-identical; shadowed now empty;
    # appended lists empty; every list re-walks cleanly
    for i, (a, b) in enumerate(zip(lists, info2["lists"])):
        sink = dict(scripts=[], contents=[], groups=[])
        mapscript.walk_tree(info2["buf"], info2["id2name"], b["ds"], b["de"], sink)
        if i in shadow_idx:
            assert not sink["scripts"] and b["de"] == b["ds"]
        else:
            assert bytes(info["buf"][a["ds"]:a["de"]]) == bytes(info2["buf"][b["ds"]:b["de"]]), i
    for b in info2["lists"][len(lists):]:
        assert b["de"] == b["ds"]
    # scb-attachability: every canonical scb player name now has a side (minus omitted)
    have = set(names2)
    assert all(n in have for n in REF_SIDES if n not in omitted)
    md5 = hashlib.md5(out).hexdigest()
    if verbose:
        print("  fixed: +sides %s%s%s; %d bytes md5=%s" %
              (adds, " | STILL MISSING (16-cap): %s" % omitted if omitted else "",
               " | emptied shadowing lists: %s" % [(n, c) for (_i, n, c) in shadowers]
               if shadowers else "", len(out), md5))
    return dict(src=src, changed=True, adds=adds, omitted=omitted,
                shadowers=[(n, c) for (_i, n, c) in shadowers], md5=md5, out=dst)

MAPS_DIR = os.path.expanduser("~/Library/Application Support/GeneralsX/GeneralsZH/Maps")
FOLDERS = ["A River Divided (2x6) V5", "2v6  Abadoned Hope", "vs5 Saddams Wrath ZH",
           "_vs5_Fluch der Karibik ZH", "4vs4 Massacre ZH", "4v4 HackePeter ZH ez",
           "White Barelands v2", "TitenWorld 8 Player", "THE World_v1",
           "4v4citylast", "Fortresses 4v4"]

def main():
    results = []
    for folder in FOLDERS:
        src_dir = os.path.join(MAPS_DIR, folder)
        mapfile = next(f for f in os.listdir(src_dir) if f.endswith(".map"))
        dst_dir = os.path.join(HERE, "staged", "fixed", folder)
        dst = os.path.join(dst_dir, mapfile)
        print("== %s" % folder)
        r = fix_map(os.path.join(src_dir, mapfile), dst)
        if r["changed"]:
            for f in os.listdir(src_dir):            # ship sibling files unchanged
                if not f.endswith(".map"):
                    shutil.copy2(os.path.join(src_dir, f), os.path.join(dst_dir, f))
        else:
            print("  unchanged (at 16-side cap or already fine); omitted: %s" % r["omitted"])
            if os.path.isdir(dst_dir):
                shutil.rmtree(dst_dir)
        results.append((folder, r))
    return results

if __name__ == "__main__":
    main()
