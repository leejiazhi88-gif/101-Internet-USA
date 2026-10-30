import urllib.request,ssl,concurrent.futures,json,pathlib
symbols=['VYLR','VMRK','P','HONA','SPCX','BSP','SKYD','SUNB','FERG','MRSH','ONC','MDLN']
def f(s):
 url=f'https://api.nasdaq.com/api/quote/{s}/company-profile?assetclass=stocks'
 try:
  d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=15));pathlib.Path('work/profiles/'+s+'.json').write_text(json.dumps(d));return s,d
 except Exception as e:return s,str(e)
with concurrent.futures.ThreadPoolExecutor(4) as ex:
 for s,d in ex.map(f,symbols):print(s,json.dumps(d,ensure_ascii=False)[:5000],flush=True)
