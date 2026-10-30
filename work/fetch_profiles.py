import urllib.request,ssl,concurrent.futures,json,pathlib,time
pool=json.load(open('work/pool.json'));root=pathlib.Path('work/profiles')
def f(x):
 s=x['ticker'];p=root/(s+'.json')
 if p.exists():return s,True
 try:
  u=f'https://api.nasdaq.com/api/company/{s}/company-profile';d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=13));p.write_text(json.dumps(d));return s,bool(d.get('data'))
 except:return s,False
with concurrent.futures.ThreadPoolExecutor(6) as ex:
 n=ok=0
 for s,b in ex.map(f,pool):
  n+=1;ok+=b
  if n%80==0:print(n,ok,flush=True)
print('done',n,ok,flush=True)
