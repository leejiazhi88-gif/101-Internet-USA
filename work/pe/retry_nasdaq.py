import urllib.request,ssl,concurrent.futures,json,pathlib,time
pool=json.load(open('work/pool.json'));jobs=[]
for x in pool:
 for k in ['annual','quarter']:
  p=pathlib.Path('work/enriched/'+x['ticker']+'_'+k+'.json')
  if not p.exists() or x['ticker']=='BRK.B':jobs.append((x['ticker'],k))
def f(z):
 s,k=z;url=f'https://api.nasdaq.com/api/company/{s}/financials?frequency='+('1' if k=='annual' else '2')
 try:
  d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=18));pathlib.Path('work/enriched/'+s+'_'+k+'.json').write_text(json.dumps(d));return s,k,bool(d.get('data'))
 except Exception as e:return s,k,str(e)
with concurrent.futures.ThreadPoolExecutor(4) as ex:
 for r in ex.map(f,jobs):print(r,flush=True)
