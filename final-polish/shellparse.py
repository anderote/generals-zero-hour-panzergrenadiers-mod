import struct
from collections import Counter
BUF = open('/private/tmp/claude-501/-Users-andrewcote-Documents-software/0d252d65-0dff-46a0-9693-2bb1e1ab748f/scratchpad/shellmap_decomp.bin','rb').read()
assert BUF[:4]==b'CkMp'
pos=4
(count,)=struct.unpack_from('<i',BUF,pos); pos+=4
id2name={}
for _ in range(count):
    ln=BUF[pos]; pos+=1
    id2name[struct.unpack_from('<I',BUF,pos+ln)[0]]=BUF[pos:pos+ln].decode('latin-1')
    pos+=ln+4
FIRST=pos
objects=[]  # (name_len_offset, slen, name)
def parse(start,end):
    p=start
    while p+10<=end:
        cid,ver,dsize=struct.unpack_from('<IHi',BUF,p)
        name=id2name.get(cid)
        if name is None or dsize<0 or p+10+dsize>end: return
        ds=p+10; de=ds+dsize
        if name=='Object':
            no=ds+20
            (slen,)=struct.unpack_from('<H',BUF,no)
            tn=BUF[no+2:no+2+slen].decode('latin-1')
            objects.append((no,slen,tn))
        if name in ('ObjectsList',): parse(ds,de)
        p=de
parse(FIRST,len(BUF))
c=Counter(n for _,_,n in objects)
# sanity: names should be printable, no newlines
bad=[n for n in c if any(ord(ch)<32 or ord(ch)>126 for ch in n)]
print("placed Objects:",len(objects),"distinct:",len(c),"bad-name:",len(bad))
print("\n== distinct placed templates ==")
for n,k in sorted(c.items()): print("  %4d  %s"%(k,n))
# save inventory
import json
json.dump(sorted(c.items()), open('/tmp/shell_inv.json','w'))
