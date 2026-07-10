import sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET
bucket = sys.argv[1]; prefix = sys.argv[2] if len(sys.argv)>2 else ''
ns = '{http://s3.amazonaws.com/doc/2006-03-01/}'
token=None; total=0; n=0; samples=[]
while True:
    url=f"http://gen.insave.ovh:9000/{bucket}?list-type=2&max-keys=1000"
    if prefix: url+="&prefix="+urllib.parse.quote(prefix, safe='')
    if token: url+="&continuation-token="+urllib.parse.quote(token.strip(), safe='')
    root=ET.fromstring(urllib.request.urlopen(url, timeout=30).read())
    for c in root.findall(ns+'Contents'):
        k=c.find(ns+'Key').text; s=int(c.find(ns+'Size').text)
        total+=s; n+=1
        if s>25_000_000: samples.append(f"  {s/1e6:9.1f} MB  {k}")
    t=root.find(ns+'NextContinuationToken')
    if root.find(ns+'IsTruncated').text=='true' and t is not None and t.text: token=t.text
    else: break
print(f"{bucket}/{prefix}: {n} objects, {total/1e9:.2f} GB total")
for s in samples[:15]: print(s)
