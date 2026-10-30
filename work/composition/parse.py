import re,json,pathlib

def obj(raw,key):
 start=raw.find(key)
 if start<0:return {}
 start=raw.find('{',start+len(key));depth=0;quote=False;escape=False;end=None
 for i in range(start,len(raw)):
  c=raw[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  else:
   if c=='"':quote=True
   elif c=='{':depth+=1
   elif c=='}':
    depth-=1
    if depth==0:end=i+1;break
 if end is None:return {}
 s=raw[start:end];parts=re.split(r'("(?:[^"\\]|\\.)*")',s)
 for i in range(0,len(parts),2):
  t=parts[i];t=re.sub(r'\bvoid\s+0\b','null',t);t=re.sub(r'([,{]\s*)([A-Za-z_$][\w$]*)(\s*:)',r'\1"\2"\3',t);t=re.sub(r'(?<=[,:\[])\.(\d)',r'0.\1',t);t=re.sub(r'(?<=[,:\[])-\.(\d)',r'-0.\1',t);parts[i]=t
 return json.loads(''.join(parts))
if __name__=='__main__':
 root=pathlib.Path('work/composition/metrics');out=pathlib.Path('work/composition/parsed');out.mkdir(exist_ok=True);n=ok=0;cats={}
 for p in root.glob('*.html'):
  n+=1
  try:
   raw=p.read_text();d=obj(raw,'financialData:');d['details']=obj(raw,'details:');d['titles']={m[0]:json.loads('"'+m[1]+'"') for m in re.findall(r'\{id:"([^"]+)",title:"((?:[^"\\]|\\.)*)"',raw)};(out/(p.stem+'.json')).write_text(json.dumps(d,ensure_ascii=False));ok+=bool(d)
   for c in d.get('categoryNames',[]):cats[c]=cats.get(c,0)+1
  except Exception as e:print(p.name,str(e)[:150])
 print(n,ok,cats)
