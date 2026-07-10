#!/usr/bin/env python3
"""Parse SkirmishScripts.scb (Zero Hour chunky script format) and report every
ScriptAction / ScriptActionFalse whose parameters reference a given set of
object type names.

Format verified against GeneralsX engine source:
  Core .../Common/System/DataChunk.cpp  (TOC + chunk headers + primitives)
  GeneralsMD .../ScriptEngine/Scripts.cpp (Script / ScriptAction / Parameter)

Chunk header: u32 LE toc-id, u16 LE version, i32 LE payload size.
Parameter: i32 type; COORD3D(17) -> 3 floats; else i32, f32, u16-len string.
ScriptAction payload (v>=2): i32 actionType, i32 nameKeyAndType(id<<8|type),
i32 numParms, params...
Script payload: 4 ascii strings, 6 bytes, (v>=2: i32 delay), nested chunks.
ScriptGroup payload: ascii string, byte, (v==2: byte), nested chunks.
"""
import struct
import sys

COORD3D = 17

# chunks whose payload is purely a sequence of nested chunks
CONTAINER_PLAIN = {"PlayerScriptsList", "ScriptList"}
# top-level chunks with non-chunk payloads (player/team dicts, waypoints...)
SKIP = {"ScriptsPlayers", "ObjectsList", "PolygonTriggers", "ScriptTeams",
        "WaypointsList"}


def read_ascii(buf, pos):
    (ln,) = struct.unpack_from("<H", buf, pos)
    pos += 2
    s = buf[pos:pos + ln].decode("latin-1")
    return s, pos + ln


def parse_param(buf, pos):
    (ptype,) = struct.unpack_from("<i", buf, pos)
    pos += 4
    if ptype == COORD3D:
        pos += 12
        return (ptype, None, None, None), pos
    (ival, rval) = struct.unpack_from("<if", buf, pos)
    pos += 8
    sval, pos = read_ascii(buf, pos)
    return (ptype, ival, rval, sval), pos


class ScbScanner:
    def __init__(self, data):
        if data[:4] != b"CkMp":
            raise ValueError("not a chunky script file")
        (count,) = struct.unpack_from("<i", data, 4)
        pos = 8
        self.names = {}
        for _ in range(count):
            ln = data[pos]
            pos += 1
            name = data[pos:pos + ln].decode("latin-1")
            pos += ln
            (cid,) = struct.unpack_from("<I", data, pos)
            pos += 4
            self.names[cid] = name
        self.data = data
        self.first_chunk = pos
        self.actions = []   # (script_name, action_kind, action_internal_name, params)
        self.scripts = 0

    def scan(self):
        self.walk(self.first_chunk, len(self.data), script=None)
        return self

    def walk(self, pos, end, script):
        d = self.data
        while pos + 10 <= end:
            cid, ver, size = struct.unpack("<IHi", d[pos:pos + 10])
            name = self.names.get(cid)
            body = pos + 10
            bend = body + size
            if name is None or bend > end:
                raise ValueError(f"bad chunk at {pos}")
            if name in CONTAINER_PLAIN:
                self.walk(body, bend, script)
            elif name == "ScriptGroup":
                p = body
                _gname, p = read_ascii(d, p)
                p += 1
                if ver == 2:
                    p += 1
                self.walk(p, bend, script)
            elif name == "Script":
                p = body
                sname, p = read_ascii(d, p)
                for _ in range(3):
                    _s, p = read_ascii(d, p)
                p += 6
                if ver >= 2:
                    p += 4
                self.scripts += 1
                self.walk(p, bend, sname)
            elif name in ("ScriptAction", "ScriptActionFalse"):
                p = body
                (_atype,) = struct.unpack_from("<i", d, p)
                p += 4
                aname = "?"
                if ver >= 2:
                    (key_and_type,) = struct.unpack_from("<i", d, p)
                    p += 4
                    aname = self.names.get(key_and_type >> 8, "?")
                (nparms,) = struct.unpack_from("<i", d, p)
                p += 4
                parms = []
                for _ in range(nparms):
                    parm, p = parse_param(d, p)
                    parms.append(parm)
                self.actions.append((script, name, aname, parms))
            # every other chunk type (OrCondition, Condition, ...) skipped
            pos = bend


def main():
    scb_path, *needles = sys.argv[1:]
    data = open(scb_path, "rb").read()
    sc = ScbScanner(data).scan()
    print(f"scripts parsed: {sc.scripts}, actions parsed: {len(sc.actions)}",
          file=sys.stderr)
    needleset = set(needles)
    for script, kind, aname, parms in sc.actions:
        strs = [p[3] for p in parms if p[3]]
        if needleset & set(strs):
            pretty = ", ".join(s for s in strs)
            print(f"{aname:45s} | script: {script!r:45s} | params: {pretty}")


if __name__ == "__main__":
    main()
