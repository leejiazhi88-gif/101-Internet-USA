import urllib.request,ssl,concurrent.futures,json,pathlib,collections,time
pool=json.load(open('work/pool.json'));dest=pathlib.Path('work/enriched');dest.mkdir(exist_ok=True)
def f(task):
 x,k=task;s=x['ticker'];p=dest/(s+'_'+k+'.json')
 if p.exists():return k,True
 sym=s.replace('.','%2F')
 paths={'history':f'quote/{sym}/historical?assetclass=stocks&fromdate=2022-06-01&todate=2026-10-27&limit=1500','summary':f'quote/{sym}/summary?assetclass=stocks','annual':f'company/{sym}/financials?frequency=1','quarter':f'company/{sym}/financials?frequency=2','forecast':f'analyst/{sym}/earnings-forecast'}
 try:
  req=urllib.request.Request('https://api.nasdaq.com/api/'+paths[k],headers={'User-Agent':'Mozilla/5.0'})
  d=json.load(urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=18));p.write_text(json.dumps(d));return k,bool(d.get('data'))
 except Exception:return k,False
jobs=[(x,k) for x in pool for k in ['history','annual','quarter','summary','forecast']]
c=collections.Counter();n=0
with concurrent.futures.ThreadPoolExecutor(12) as ex:
 for k,ok in ex.map(f,jobs):
  c[(k,ok)]+=1;n+=1
  if n%200==0:print('done',n,'/',len(jobs),flush=True)
print(c,flush=True)
