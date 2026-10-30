import urllib.request,ssl,json,concurrent.futures
urls={'nvda_info':'https://api.nasdaq.com/api/quote/NVDA/info?assetclass=stocks','nvda_summary':'https://api.nasdaq.com/api/quote/NVDA/summary?assetclass=stocks','nvda_forecast':'https://query1.finance.yahoo.com/v10/finance/quoteSummary/NVDA?modules=earningsTrend,financialData','gics':'https://en.wikipedia.org/wiki/Global_Industry_Classification_Standard'}
def f(z):
 k,u=z
 try:
  h=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=20).read().decode();open('work/'+k+'.txt','w').write(h);return k,len(h),h[:1200]
 except Exception as e:return k,str(e)
with concurrent.futures.ThreadPoolExecutor(4) as e:
 for x in e.map(f,urls.items()):print(x,flush=True)
