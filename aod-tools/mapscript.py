#!/usr/bin/env python3
"""Generalized ZH .map decoder/analyzer for the AOD lab.

Handles: EAR/RefPack compressed maps, symbol table, SidesList v2/v3 (with
non-empty buildlists), team dicts, PlayerScriptsList trees (ScriptGroup v1/v2,
Script v1/v2, Condition v1..v4, ScriptAction[False] v1/v2), ObjectsList.
Enum->name tables for old chunk versions come from the engine's Scripts.h
(script_enums.json, generated).  Parameter wire format per Scripts.h:
UNIT=14, OBJECT_TYPE=15, COORD3D=16 (3 floats), ANGLE=17.
"""
import os, sys, struct, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/andrewcote/Documents/software/generalsx-mods/final-polish")
sys.path.insert(0, "/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon")
from refpack import strip_ear, refpack_decompress

_E = json.load(open(os.path.join(HERE, "script_enums.json")))
ACTION_NAMES = {int(k): v for k, v in _E["actions"].items()}
COND_NAMES = {int(k): v for k, v in _E["conditions"].items()}

P_INT, P_REAL, P_SCRIPT, P_TEAM, P_COUNTER, P_FLAG, P_COMPARISON, P_WAYPOINT = range(8)
P_BOOLEAN, P_TRIGGER_AREA, P_TEXT_STRING, P_SIDE, P_SOUND, P_SUBROUTINE = range(8, 14)
P_UNIT, P_OBJECT_TYPE, P_COORD3D, P_ANGLE = 14, 15, 16, 17

def load_map(path):
    raw = open(path, "rb").read()
    if raw[:4] == b"CkMp":
        return raw
    stream, _ = strip_ear(raw)
    buf, _ = refpack_decompress(stream)
    assert buf[:4] == b"CkMp", "not a map: %s" % path
    return buf

def rd_ascii(buf, p):
    (n,) = struct.unpack_from("<H", buf, p); p += 2
    return buf[p:p+n].decode("latin-1"), p + n

def read_dict(b, p):
    (npairs,) = struct.unpack_from("<H", b, p); p += 2
    pairs = []
    for _ in range(npairs):
        (packed,) = struct.unpack_from("<I", b, p); p += 4
        keyid, typ = packed >> 8, packed & 0xFF
        if typ == 0:   v = b[p]; p += 1
        elif typ == 1: v = struct.unpack_from("<i", b, p)[0]; p += 4
        elif typ == 2: v = struct.unpack_from("<f", b, p)[0]; p += 4
        elif typ == 3:
            (sl,) = struct.unpack_from("<H", b, p); p += 2
            v = b[p:p+sl].decode("latin-1"); p += sl
        elif typ == 4:
            (sl,) = struct.unpack_from("<H", b, p); p += 2
            v = b[p:p+2*sl].decode("utf-16-le", "replace"); p += 2*sl
        else: raise ValueError("bad dict type %d @%d" % (typ, p))
        pairs.append((keyid, typ, v))
    return pairs, p

def parse_map(buf):
    assert buf[:4] == b"CkMp"
    pos = 4
    (count,) = struct.unpack_from("<i", buf, pos); pos += 4
    id2name = {}
    for _ in range(count):
        ln = buf[pos]; pos += 1
        id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
        pos += ln + 4
    data_start = pos
    top, p = [], data_start
    while p + 10 <= len(buf):
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        nm = id2name.get(cid)
        if nm is None or dsize < 0 or p+10+dsize > len(buf):
            raise ValueError("bad top-level chunk @%d" % p)
        top.append(dict(nm=nm, ver=ver, dsize=dsize, hp=p, ds=p+10, de=p+10+dsize))
        p += 10 + dsize
    assert p == len(buf)
    return id2name, {v: k for k, v in id2name.items()}, data_start, top

def walk_sides(buf, sl, id2name):
    """SidesList v>=2. Returns sides, buildlists, teams, psl info, script lists."""
    p = sl["ds"]
    (nsides,) = struct.unpack_from("<i", buf, p); p += 4
    sides, builds = [], []
    for _ in range(nsides):
        pairs, p = read_dict(buf, p)
        (nb,) = struct.unpack_from("<i", buf, p); p += 4
        bl = []
        for _ in range(nb):
            bn, p = rd_ascii(buf, p); tn, p = rd_ascii(buf, p)
            p += 16      # x, y, z, angle
            p += 1 + 4   # initiallyBuilt, numRebuilds
            if sl["ver"] >= 3:
                scr, p = rd_ascii(buf, p)
                p += 4 + 1 + 1 + 1   # health, whiner, unsellable, repairable
            else:
                scr = ""
            bl.append((bn, tn, scr))
        sides.append({id2name.get(k, k): v for (k, _t, v) in pairs})
        builds.append(bl)
    teams_cnt_off = p
    teams = []
    if sl["ver"] >= 2:
        (nteams,) = struct.unpack_from("<i", buf, p); p += 4
        for _ in range(nteams):
            t0 = p
            pairs, p = read_dict(buf, p)
            teams.append((t0, p, {id2name.get(k, k): v for (k, _t, v) in pairs}))
    psl_hp = p
    cid, psl_ver, dsize = struct.unpack_from("<IHi", buf, p)
    assert id2name.get(cid) == "PlayerScriptsList", "expected PlayerScriptsList @%d" % p
    psl_ds, psl_de = p + 10, p + 10 + dsize
    assert psl_de == sl["de"]
    lists, q = [], psl_ds
    while q < psl_de:
        cid2, lver, ds2 = struct.unpack_from("<IHi", buf, q)
        assert id2name.get(cid2) == "ScriptList", "expected ScriptList @%d" % q
        lists.append(dict(hp=q, ver=lver, ds=q+10, de=q+10+ds2))
        q += 10 + ds2
    assert q == psl_de
    return sides, builds, teams_cnt_off, teams, dict(hp=psl_hp, ver=psl_ver, ds=psl_ds, de=psl_de), lists

def parse_content(buf, id2name, nm, ver, ds, de):
    """Condition / ScriptAction[False] payload -> (type_name, parms)."""
    q = ds
    (enum,) = struct.unpack_from("<i", buf, q); q += 4
    name = None
    need_key = (nm == "Condition" and ver >= 4) or (nm != "Condition" and ver >= 2)
    if need_key:
        (keyraw,) = struct.unpack_from("<I", buf, q); q += 4
        assert keyraw & 0xFF == 3
        name = id2name.get(keyraw >> 8)
    if name is None:
        name = (COND_NAMES if nm == "Condition" else ACTION_NAMES).get(enum, "?%d" % enum)
    (nparms,) = struct.unpack_from("<i", buf, q); q += 4
    parms = []
    for _ in range(nparms):
        (ptype,) = struct.unpack_from("<i", buf, q); q += 4
        if ptype == P_COORD3D:
            x, y, z = struct.unpack_from("<fff", buf, q); q += 12
            parms.append((ptype, 0, 0.0, "(%.0f,%.0f,%.0f)" % (x, y, z)))
        else:
            (pi,) = struct.unpack_from("<i", buf, q); q += 4
            (pr,) = struct.unpack_from("<f", buf, q); q += 4
            ps, q = rd_ascii(buf, q)
            parms.append((ptype, pi, pr, ps))
    assert q == de, "%s v%d payload end %d != %d" % (nm, ver, q, de)
    return enum, name, parms

def walk_tree(buf, id2name, start, end, sink, group="", script=None):
    p = start
    while p < end:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        nm = id2name.get(cid)
        ds, de = p + 10, p + 10 + dsize
        assert de <= end and dsize >= 0, "chunk overrun @%d" % p
        q = ds
        if nm == "ScriptGroup":
            gname, q = rd_ascii(buf, q)
            gact = buf[q]; q += 1
            gsub = buf[q] if ver >= 2 else 0
            q += 1 if ver >= 2 else 0
            sink["groups"].append((gname, gact, gsub))
            walk_tree(buf, id2name, q, de, sink, group=gname)
        elif nm == "Script":
            sname, q = rd_ascii(buf, q)
            cmts = []
            for _ in range(3):
                c, q = rd_ascii(buf, q); cmts.append(c)
            flags = bytes(buf[q:q+6]); q += 6
            delay = 0
            if ver >= 2:
                (delay,) = struct.unpack_from("<i", buf, q); q += 4
            rec = dict(name=sname, group=group, flags=flags, delay=delay,
                       ds=ds, de=de, conds=[], actions=[], false_actions=[])
            sink["scripts"].append(rec)
            walk_tree(buf, id2name, q, de, sink, group=group, script=rec)
        elif nm == "OrCondition":
            walk_tree(buf, id2name, q, de, sink, group=group, script=script)
        elif nm in ("Condition", "ScriptAction", "ScriptActionFalse"):
            enum, name, parms = parse_content(buf, id2name, nm, ver, ds, de)
            sink["contents"].append((nm, name, parms))
            if script is not None:
                key = {"Condition": "conds", "ScriptAction": "actions",
                       "ScriptActionFalse": "false_actions"}[nm]
                script[key].append((name, parms))
        else:
            raise AssertionError("unexpected %r in script tree @%d" % (nm, p))
        p = de
    assert p == end

def parse_objects(buf, ol):
    objs, p = [], ol["ds"]
    while p + 10 <= ol["de"]:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        ds, de = p + 10, p + 10 + dsize
        x, y, z, ang = struct.unpack_from("<ffff", buf, ds)
        (slen,) = struct.unpack_from("<H", buf, ds + 20)
        tn = buf[ds+22:ds+22+slen].decode("latin-1")
        pairs, dend = read_dict(buf, ds + 22 + slen)
        assert dend == de, "object dict end mismatch @%d" % p
        objs.append(dict(tn=tn, x=x, y=y, ang=ang, pairs=pairs,
                         d={k: v for (k, _t, v) in pairs}, hp=p, ds=ds, de=de))
        p = de
    assert p == ol["de"]
    return objs

def analyze(path):
    """Full decode -> dict with everything the playbook/vet needs."""
    buf = load_map(path)
    id2name, name2id, data_start, top = parse_map(buf)
    sl = [t for t in top if t["nm"] == "SidesList"][0]
    sides, builds, tco, teams, psl, lists = walk_sides(buf, sl, id2name)
    sink = dict(groups=[], scripts=[], contents=[])
    for l in lists:
        walk_tree(buf, id2name, l["ds"], l["de"], sink)
    ol = [t for t in top if t["nm"] == "ObjectsList"][0]
    objs = parse_objects(buf, ol)
    waypoints = {}
    for o in objs:
        for (k, _t, v) in o["pairs"]:
            if id2name.get(k) == "waypointName" and v:
                waypoints[v] = (o["x"], o["y"])
    return dict(buf=buf, id2name=id2name, name2id=name2id, data_start=data_start,
                top=top, sl=sl, sides=sides, builds=builds, teams_cnt_off=tco,
                teams=teams, psl=psl, lists=lists, sink=sink, objs=objs,
                waypoints=waypoints)

def referenced_templates(info):
    """Every object-template string a map needs: placed objects, team unit types,
    OBJECT_TYPE script params, buildlist templates."""
    refs = {}
    def add(t, why):
        if t and t != "<none>":
            refs.setdefault(t, set()).add(why)
    for o in info["objs"]:
        if not o["tn"].startswith("*"):
            add(o["tn"], "placed")
    for (_a, _b, d) in info["teams"]:
        for i in range(1, 8):
            add(d.get("teamUnitType%d" % i), "team")
    for (_nm, name, parms) in info["sink"]["contents"]:
        for (pt, _i, _r, s) in parms:
            if pt == P_OBJECT_TYPE:
                add(s, "script")
    for bl in info["builds"]:
        for (_bn, tn, _scr) in bl:
            add(tn, "buildlist")
    return refs

def dump(path, out=sys.stdout, max_parm=110):
    info = analyze(path)
    w = out.write
    w("=" * 100 + "\nMAP: %s  (%d bytes decompressed, %d symbols)\n" %
      (os.path.basename(path), len(info["buf"]), len(info["id2name"])))
    w("top: %s\n" % [t["nm"] for t in info["top"]])
    for i, sd in enumerate(info["sides"]):
        w("side[%d] %r faction=%r human=%r allies=%r enemies=%r builds=%d\n" % (
            i, sd.get("playerName"), sd.get("playerFaction"), sd.get("playerIsHuman"),
            sd.get("playerAllies"), sd.get("playerEnemies"), len(info["builds"][i])))
    w("teams: %d\n" % len(info["teams"]))
    for (_a, _b, d) in info["teams"]:
        units = ", ".join("%dx %s" % (d.get("teamUnitMaxCount%d" % i, 0), d["teamUnitType%d" % i])
                          for i in range(1, 8)
                          if d.get("teamUnitType%d" % i) and d.get("teamUnitType%d" % i) != "<none>")
        extra = "".join(" %s=%r" % (k, d[k]) for k in
                        ("teamOnCreateScript", "teamOnDestroyedScript", "teamOnIdleScript",
                         "teamEnemySightedScript", "teamProductionCondition", "teamVeterancy",
                         "teamMaxInstances", "teamHome", "teamReinforcementOrigin")
                        if d.get(k) not in (None, "", 0))
        w("  TEAM %-34r owner=%-18r %s%s\n" % (d.get("teamName"), d.get("teamOwner"), units, extra))
    w("script lists: %d ; groups: %d ; scripts: %d\n" %
      (len(info["lists"]), len(info["sink"]["groups"]), len(info["sink"]["scripts"])))
    for rec in info["sink"]["scripts"]:
        fl = rec["flags"]
        w("  SCRIPT %-40r grp=%-24r act=%d 1shot=%d enh=%d%d%d sub=%d delay=%d\n" %
          (rec["name"], rec["group"], fl[0], fl[1], fl[2], fl[3], fl[4], fl[5], rec["delay"]))
        for (name, parms) in rec["conds"]:
            w("      IF   %-36s %s\n" % (name, fmt_parms(parms, max_parm)))
        for (name, parms) in rec["actions"]:
            w("      DO   %-36s %s\n" % (name, fmt_parms(parms, max_parm)))
        for (name, parms) in rec["false_actions"]:
            w("      ELSE %-36s %s\n" % (name, fmt_parms(parms, max_parm)))
    return info

def fmt_parms(parms, maxlen=110):
    bits = []
    for (pt, pi, pr, ps) in parms:
        if ps: bits.append(repr(ps))
        elif pt == P_REAL or (pr and abs(pr) > 1e-9): bits.append("%.2f" % pr)
        else: bits.append(str(pi))
    txt = ", ".join(bits)
    return txt if len(txt) <= maxlen else txt[:maxlen] + "..."

if __name__ == "__main__":
    for m in sys.argv[1:]:
        dump(m)
