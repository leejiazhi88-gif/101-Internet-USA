import urllib.request,ssl,concurrent.futures,json
urls={'earnings_forecast':'https://api.nasdaq.com/api/analyst/NVDA/earnings-forecast','pe':'https://api.nasdaq.com/api/quote/NVDA/pe-ratio?assetclass=stocks','historical':'https://api.nasdaq.com/api/quote/NVDA/historical?assetclass=stocks&fromdate=2023-01-01&todate=2026-10-27&limit=1500'}
def f(z):
 k,u=z
 try:
  h=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=20).read().decode();open('work/probe_'+k+'.json','w').write(h);return k,len(h),h[:1600]
 except Exception as e:return k,str(e)
with concurrent.futures.ThreadPoolExecutor(3) as ex:
 for r in ex.map(f,urls.items()):print(r,flush=True)
