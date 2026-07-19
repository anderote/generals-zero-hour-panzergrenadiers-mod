#!/usr/bin/env python3
"""Universal ZH .map decoder: works on ANY map by reading its own symbol table.
Reports dimensions + height flatness, blend texture names (grass?), top-level
chunk tree, SidesList players/teams/hostility, object count, and waypoint name
encoding (esp. InitialCameraPosition). Handles compressed & uncompressed maps."""
import os, sys, struct, glob, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon")); sys.path.insert(0, HERE)
from bigfile import read_big
from refpack import strip_ear, refpack_decompress

def decode_map_bytes(raw):
    if raw[:4] == b"CkMp":
        return raw
    stream, _ = strip_ear(raw)
    buf, _ = refpack_decompress(stream)
    return buf

def find_map(mappath_substr):
    dirs = [os.path.expanduser("~/GeneralsX/GeneralsZH"),
            os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
            os.path.expanduser("~/GeneralsX/mods/ShockWave")]
    for d in dirs:
        for b in glob.glob(os.path.join(d, "*.big")):
            try: ents = read_big(b)
            except: continue
            for e in ents:
                if mappath_substr.lower() in e.path.lower() and e.path.lower().endswith(".map"):
                    return e.path, os.path.basename(b), decode_map_bytes(e.data)
    return None, None, None

def read_dict(b, p):
    (npairs,) = struct.unpack_from("<H", b, p); p += 2
    d = {}
    for _ in range(npairs):
        (packed,) = struct.unpack_from("<I", b, p); p += 4
        keyid = packed >> 8; typ = packed & 0xFF
        if typ == 0: v = b[p]; p += 1
        elif typ == 1: v = struct.unpack_from("<i", b, p)[0]; p += 4
        elif typ == 2: v = struct.unpack_from("<f", b, p)[0]; p += 4
        elif typ == 3:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+sl].decode("latin-1"); p += sl
        elif typ == 4:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+2*sl].decode("latin-1","replace"); p += 2*sl
        else: raise ValueError("bad dict type %d @%d" % (typ, p))
        d[keyid] = v
    return d, p

def decode(mapsubstr):
    path, owner, buf = find_map(mapsubstr)
    if buf is None:
        print("NOT FOUND:", mapsubstr); return
    print("="*90); print("MAP:", path, " owner:", owner, " uncompressed:", len(buf))
    assert buf[:4] == b"CkMp"
    pos = 4
    (count,) = struct.unpack_from("<i", buf, pos); pos += 4
    id2name = {}
    for _ in range(count):
        ln = buf[pos]; pos += 1
        id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
        pos += ln + 4
    name2id = {v: k for k, v in id2name.items()}
    DS = pos
    # top-level walk
    top = []
    p = DS
    while p + 10 <= len(buf):
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        nm = id2name.get(cid)
        if nm is None or dsize < 0 or p+10+dsize > len(buf):
            print("  <bad chunk @%d>" % p); break
        top.append((nm, ver, dsize, p+10, p+10+dsize)); p = p+10+dsize
    print("  symbols:", count, " top-level:", [t[0] for t in top])

    # HeightMapData
    hm = next((t for t in top if t[0]=="HeightMapData"), None)
    if hm:
        _,ver,dsize,ds,de = hm; q = ds
        w = struct.unpack_from("<i",buf,q)[0]; q+=4
        h = struct.unpack_from("<i",buf,q)[0]; q+=4
        border = 0
        if ver>=3: border = struct.unpack_from("<i",buf,q)[0]; q+=4
        if ver>=4:
            nb = struct.unpack_from("<i",buf,q)[0]; q+=4; q += nb*8
        datasize = struct.unpack_from("<i",buf,q)[0]; q+=4
        data = buf[q:q+datasize]
        hs = list(data)
        var = statistics.pstdev(hs) if len(hs)>1 else 0
        frac_flat = sum(1 for v in hs if abs(v-hs[0])<=1)/len(hs) if hs else 0
        print("  HeightMap: %dx%d border=%d dataSize=%d  height[min=%d max=%d mean=%.1f stdev=%.2f]  flatfrac=%.2f"
              % (w,h,border,datasize,min(hs),max(hs),sum(hs)/len(hs),var,frac_flat))

    # BlendTileData -> texture name strings (readable ascii)
    bt = next((t for t in top if t[0]=="BlendTileData"), None)
    if bt:
        _,_,_,ds,de = bt
        blob = buf[ds:de]
        import re
        names = re.findall(rb"[A-Za-z][A-Za-z0-9_ ]{3,40}", blob)
        seen=[];
        for n in names:
            s=n.decode("latin-1")
            if s not in seen and not s.isdigit(): seen.append(s)
        tex=[s for s in seen if any(k in s.lower() for k in
             ("grass","dirt","sand","rock","road","snow","cliff","gras","field","desert","water","tundra","road","terrain","blend"))]
        print("  BlendTile textures (filtered):", tex[:14])

    # SidesList players + hostility
    sl = next((t for t in top if t[0]=="SidesList"), None)
    if sl:
        _,ver,dsize,ds,de = sl
        q = ds; (nsides,) = struct.unpack_from("<i",buf,q); q+=4
        print("  SidesList v%d nsides=%d"%(ver,nsides))
        for i in range(nsides):
            try:
                d,q = read_dict(buf,q)
            except Exception as ex:
                print("    side parse stop @%d: %s"%(q,ex)); break
            (nb,) = struct.unpack_from("<i",buf,q); q+=4
            nm=d.get(name2id.get("playerName",8)) if False else d.get(8)
            # keyids: 8 playerName,11 faction,12 allies,13 enemies (may differ per map!)
            print("    side[%d] name=%r faction=%r allies=%r enemies=%r buildlists=%d"%(
                i, d.get(name2id.get("playerName")), d.get(name2id.get("playerFaction")),
                d.get(name2id.get("playerAllies")), d.get(name2id.get("playerEnemies")), nb))
            if nb!=0:
                print("       (buildlists present -> stopping detailed side parse)"); break

    # ObjectsList: count + waypoint dict encoding + InitialCameraPosition
    ol = next((t for t in top if t[0]=="ObjectsList"), None)
    if ol:
        _,_,_,ds,de = ol; q=ds; nobj=0; wp=[]; initcam=None; sampledict=None
        while q+10<=de:
            cid,ver2,ds2 = struct.unpack_from("<IHi",buf,q)
            if id2name.get(cid)!="Object": break
            a=q+10
            x,y,z,ang = struct.unpack_from("<ffff",buf,a)
            (slen,)=struct.unpack_from("<H",buf,a+20); tn=buf[a+22:a+22+slen].decode("latin-1")
            dd,_=read_dict(buf,a+22+slen)
            if sampledict is None: sampledict=(tn,dd)
            if "Waypoint" in tn:
                # find a string value == InitialCameraPosition
                for k,v in dd.items():
                    if isinstance(v,str) and "InitialCamera" in v:
                        initcam=(x,y,z,k,dict(dd));
                if len(wp)<3: wp.append((tn,x,y,dict(dd)))
            nobj+=1; q=a+ds2
        print("  ObjectsList: %d objects"%nobj)
        print("    sample object dict:", sampledict[0] if sampledict else None,
              {k:v for k,v in (sampledict[1].items() if sampledict else [])})
        if wp: print("    sample waypoint:", wp[0])
        print("    InitialCameraPosition:", (initcam[0],initcam[1],initcam[2],"keyid=",initcam[3]) if initcam else "NOT FOUND")
        if initcam: print("       initcam dict:", initcam[4])

    # print dict nameKey ids we care about
    for nm in ("playerName","playerAllies","playerEnemies","teamName","originalOwner",
               "objectInitialHealth","uniqueID","objectName","waypointID","waypointName"):
        if nm in name2id: print("    nameKeyid[%s]=%d"%(nm,name2id[nm]))

if __name__ == "__main__":
    for m in sys.argv[1:]:
        decode(m)
