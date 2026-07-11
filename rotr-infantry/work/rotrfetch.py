"""Ranged-HTTP fetcher for the ROTR .gib (renamed BIGF) archives on
gen.insave.ovh.  We never download the big archives whole: a Range
request grabs the 16-byte header, a second grabs the index table, and
each needed file is then fetched by its exact byte range.  Everything is
cached under rotr-infantry/cache/ (indexes as JSON, files under
cache/fetched/<archive>/) so rebuilds and future ROTR ports are offline.

Archive preference for duplicate paths (newest ROTR hotfix layer first,
matching the original engine's first-archive-wins load order that ROTR's
!!!/!!/! naming scheme is built around):
    !!!Rotr_Intrnl_Main.gib > !!Rotr_Patch.gib > !Rotr_W3D.gib /
    !Rotr_Textures.gib / !Rotr_2D.gib / !Rotr_English.gib
"""
import json
import os
import ssl
import struct
import urllib.request

BASE = "http://gen.insave.ovh:9000/rotr/rotr-individual-files/"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.abspath(os.path.join(HERE, "..", "cache"))

# preference order: earlier archives win for duplicate internal paths
ARCHIVES = [
    "!!!Rotr_Intrnl_Main.gib",
    "!!Rotr_Patch.gib",
    "!Rotr_W3D.gib",
    "!Rotr_Textures.gib",
    "!Rotr_2D.gib",
    "!Rotr_English.gib",
]


def _get_range(url, start, end):
    req = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (start, end)})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    want = end - start + 1
    if len(data) != want:
        raise IOError("ranged fetch %s [%d-%d]: got %d bytes, wanted %d"
                      % (url, start, end, len(data), want))
    return data


def load_index(archive):
    """Return list of (path, offset, size) for a .gib, via 2 ranged GETs."""
    os.makedirs(CACHE, exist_ok=True)
    cache_fp = os.path.join(CACHE, "gibindex_%s.json" % archive.strip("!").replace(".gib", ""))
    if os.path.exists(cache_fp):
        with open(cache_fp) as f:
            return [tuple(e) for e in json.load(f)]
    url = BASE + urllib.request.quote(archive)
    head = _get_range(url, 0, 15)
    if head[:4] != b"BIGF":
        raise ValueError("%s: not a BIGF archive (%r)" % (archive, head[:4]))
    (num_files,) = struct.unpack_from(">I", head, 8)
    (header_size,) = struct.unpack_from(">I", head, 12)
    table = _get_range(url, 16, header_size - 1)
    entries = []
    pos = 0
    for _ in range(num_files):
        offset, size = struct.unpack_from(">II", table, pos)
        pos += 8
        end = table.index(b"\x00", pos)
        name = table[pos:end].decode("latin-1")
        pos = end + 1
        entries.append((name, offset, size))
    with open(cache_fp, "w") as f:
        json.dump(entries, f)
    print("  indexed %s: %d files" % (archive, num_files))
    return entries


class RotrArt:
    def __init__(self, archives=ARCHIVES):
        self.archives = archives
        self._maps = {}     # archive -> {lower path: (path, offset, size)}

    def _map(self, archive):
        if archive not in self._maps:
            m = {}
            for path, off, size in load_index(archive):
                m[path.lower().replace("/", "\\")] = (path, off, size)
            self._maps[archive] = m
        return self._maps[archive]

    def find(self, basename_or_path):
        """Find a file by basename (searched anywhere) or full internal path.
        Returns (archive, path, offset, size) or None.  Preference order wins."""
        want = basename_or_path.lower().replace("/", "\\")
        for archive in self.archives:
            m = self._map(archive)
            if "\\" in want:
                if want in m:
                    p, o, s = m[want]
                    return archive, p, o, s
            else:
                for k, (p, o, s) in m.items():
                    if k.rsplit("\\", 1)[-1] == want:
                        return archive, p, o, s
        return None

    def fetch(self, basename_or_path):
        """Fetch a file (cached).  Returns (internal_path, local_path)."""
        hit = self.find(basename_or_path)
        if hit is None:
            raise KeyError(basename_or_path)
        archive, path, off, size = hit
        sub = archive.strip("!").replace(".gib", "")
        local = os.path.join(CACHE, "fetched", sub, path.replace("\\", "/"))
        if not (os.path.exists(local) and os.path.getsize(local) == size):
            os.makedirs(os.path.dirname(local), exist_ok=True)
            url = BASE + urllib.request.quote(archive)
            data = _get_range(url, off, off + size - 1)
            with open(local, "wb") as f:
                f.write(data)
            print("  fetched %s <- %s (%d bytes)" % (path, archive, size))
        return path, local


if __name__ == "__main__":
    import sys
    art = RotrArt()
    for name in sys.argv[1:]:
        hit = art.find(name)
        print(name, "->", hit)
