import urllib.request,concurrent.futures,re,ssl
urls=['https://site.financialmodelingprep.com/developer/docs/pricing','https://site.financialmodelingprep.com/developer/docs/stable/analyst-estimates','https://eodhd.com/financial-apis/stock-etfs-fundamental-data-feeds','https://eodhd.com/pricing','https://www.alphavantage.co/documentation/','https://mcp.alphavantage.co/','https://finnhub.io/docs/api','https://finnhub.io/pricing','https://massive.com/docs','https://www.factset.com/marketplace/catalog/product/factset-estimates-api','https://www.sec.gov/search-filings/edgar-application-programming-interfaces','https://github.com/financial-datasets/mcp-server','https://eodhd.com/financial-apis/mcp-server-for-financial-data']
def go(u):
 try:
  r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=25);h=r.read().decode();t=re.sub('<[^>]+>',' ',re.sub(r'<(script|style)\b.*?</\1>','',h,flags=re.S));t=re.sub(r'\s+',' ',t);fn='work/'+re.sub(r'[^a-zA-Z0-9]','_',u)+'.txt';open(fn,'w').write(t);return u,r.status,len(t),fn
 except Exception as e:return u,str(e)
with concurrent.futures.ThreadPoolExecutor(13) as ex:
 for f in concurrent.futures.as_completed([ex.submit(go,u) for u in urls]):print(f.result(),flush=True)
