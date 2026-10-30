import urllib.request,ssl,pathlib,re,html,json,concurrent.futures
urls={'skhynix_pe':'https://companiesmarketcap.com/sk-hynix/pe-ratio/','skhynix_cap':'https://companiesmarketcap.com/sk-hynix/marketcap/','skhynix_earnings':'https://companiesmarketcap.com/sk-hynix/earnings/'}
def f(kv):
 k,u=kv
 try:
  raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=20).read().decode();pathlib.Path('work/pe/'+k+'.html').write_text(raw)
  txt=html.unescape(re.sub('<[^>]+>',' ',raw));txt=re.sub(r'\s+',' ',txt)
  for term in ['P/E ratio for','Market cap:','Earnings for']:
   m=txt.find(term)
   if m>=0:print(k,txt[m:m+1600],flush=True)
  m=re.search(r'data = (\[.*?\]);',raw)
  if m:print(k,'lastpoints',json.loads(m.group(1))[-3:],flush=True)
 except Exception as e:print(k,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(f,urls.items()))
