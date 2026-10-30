import urllib.request,ssl,concurrent.futures,json,pathlib
pool=json.load(open('work/pool.json'));dest=pathlib.Path('work/quote_info');dest.mkdir(exist_ok=True)
def f(x):
 s=x['ticker'];p=dest/(s+'.json')
 if p.exists():return True
 try:
  u='https://api.nasdaq.com/api/quote/'+s.replace('.','%2F')+'/info?assetclass=stocks';d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=15));p.write_text(json.dumps(d));return bool(d.get('data'))
 except Exception:return False
with concurrent.futures.ThreadPoolExecutor(12) as ex:
 vals=list(ex.map(f,pool))
print('quotes succeeded',sum(vals),'of',len(vals),flush=True)
from collections import Counter
c=Counter()
for p in dest.glob('*.json'):
 d=json.load(p.open()).get('data') or {};c[(d.get('primaryData') or {}).get('lastTradeTimestamp','missing')]+=1
print(c)
