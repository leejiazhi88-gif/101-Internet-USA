import json,urllib.request,ssl,concurrent.futures,pathlib,time
pool=json.load(open('work/pool.json'));root=pathlib.Path('work/composition/sa');root.mkdir(exist_ok=True)
def f(x):
 s=x['ticker'];p=root/(s+'.html')
 if p.exists():return True
 try:
  u=f'https://stockanalysis.com/stocks/{s.lower().replace(".","-")}/revenue/'
  raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Research contact research@example.com','Accept-Encoding':'identity'}),context=ssl._create_unverified_context(),timeout=18).read().decode();p.write_text(raw);time.sleep(.15);return True
 except:return False
with concurrent.futures.ThreadPoolExecutor(6) as ex:
 n=ok=0
 for b in ex.map(f,pool):
  n+=1;ok+=b
  if n%50==0:print(n,ok,flush=True)
print('done',n,ok)
