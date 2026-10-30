import pathlib,json,urllib.request,ssl,re,html,concurrent.futures
root=pathlib.Path('work/pe/cmc');mapping=json.load(open('work/pe/cmc_map.json'));r=json.load(open('work/pe/prepared.json'));jobs=[]
for x in r:
 if x['pe']!='缺可用TTM数据':continue
 s=x['ticker'];p=root/(s+'.json')
 if p.exists():
  d=json.loads(p.read_text())
  if d.get('error') and any(w in d['error'] for w in ['timed out','reset']):jobs.append(s)
def f(s):
 url='https://companiesmarketcap.com'+mapping[s].replace('/marketcap/','/pe-ratio/')
 try:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=22).read().decode();m=re.search(r'data = (\[.*?\]);',raw)
  d={'symbol':s,'url':url,'history':json.loads(m.group(1)) if m else [],'text':html.unescape(re.sub('<[^>]+>',' ',raw))};(root/(s+'.json')).write_text(json.dumps(d));return s,len(d['history'])
 except Exception as e:return s,str(e)
with concurrent.futures.ThreadPoolExecutor(3) as ex:
 for x in ex.map(f,jobs):print(x,flush=True)
