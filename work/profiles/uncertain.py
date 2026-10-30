import json,urllib.request,ssl,re,pathlib,concurrent.futures,html
m=json.load(open('work/pe/cmc_map.json'));syms=['VYLR','VMRK','P','HONA','SUNB','BSP','SKYD','MRSH']
def f(s):
 link=m.get(s)
 if not link:return s,'no mapping'
 url='https://companiesmarketcap.com'+link
 try:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=18).read().decode();txt=html.unescape(re.sub('<[^>]+>',' ',raw));txt=re.sub(r'\s+',' ',txt);pathlib.Path('work/profiles/'+s+'.txt').write_text(txt)
  return s,txt[txt.find('Market cap:'):txt.find('Market cap:')+1800],re.findall(r'<meta[^>]+name="description"[^>]+>',raw),link
 except Exception as e:return s,str(e)
with concurrent.futures.ThreadPoolExecutor(4) as ex:
 for r in ex.map(f,syms):print(r,flush=True)
