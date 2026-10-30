import urllib.request,ssl,json,pathlib,concurrent.futures

def f(s):
 try:
  req=urllib.request.Request('https://api.nasdaq.com/api/quote/'+s+'/info?assetclass=stocks',headers={'User-Agent':'Mozilla/5.0'})
  d=json.load(urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=15))
  if d.get('data'):
   symbol='BRK.B' if s.startswith('BRK') else s
   pathlib.Path('work/quote_info/'+symbol+'.json').write_text(json.dumps(d))
   print(s,d['data'].get('primaryData',{}).get('lastTradeTimestamp'),flush=True)
 except Exception as e:print(s,type(e).__name__,flush=True)
with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(f,['BEKE','BRK.B','BRK-B']))
