import urllib.request,ssl,pathlib,re,json,html,concurrent.futures,time,datetime
root=pathlib.Path('work/pe/cmc');root.mkdir(exist_ok=True)
def get(url):
 r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=ssl._create_unverified_context(),timeout=18);return r.read().decode()
def page(n):
 p=root/f'list_{n}.html'
 try:
  s=p.read_text() if p.exists() else get('https://companiesmarketcap.com/?page='+str(n));p.write_text(s);return s
 except:return ''
mapping={}
with concurrent.futures.ThreadPoolExecutor(3) as ex:
 for s in ex.map(page,range(1,17)):
  for row in re.findall(r'<tr>(.*?)</tr>',s,re.S):
   link=re.search(r'href="(/[^"/]+/marketcap/)"',row);code=re.search(r'class="company-code">(.*?)</div>',row,re.S)
   if link and code:mapping[html.unescape(re.sub('<[^>]+>','',code.group(1))).strip()]=link.group(1)
pathlib.Path('work/pe/cmc_map.json').write_text(json.dumps(mapping));print('mapped',len(mapping),flush=True)
needed={x['ticker'] for x in json.load(open('work/pe/prepared.json')) if x['pe']=='缺可用TTM数据'}
pool=[x for x in json.load(open('work/pool.json')) if x['ticker'] in needed]
def f(x):
 sym=x['ticker'];link=mapping.get(sym) or mapping.get(sym.replace('.','-'))
 if not link:return False
 p=root/(sym+'.json')
 if p.exists():return True
 url='https://companiesmarketcap.com'+link.replace('/marketcap/','/pe-ratio/')
 try:
  s=get(url);m=re.search(r'data = (\[.*?\]);',s);a=json.loads(m.group(1)) if m else []
  prices=re.findall(r'class="price"[^>]*>(.*?)</',s,re.S)
  p.write_text(json.dumps({'symbol':sym,'url':url,'history':a,'prices':prices,'text':html.unescape(re.sub('<[^>]+>',' ',s))},ensure_ascii=False));time.sleep(.3);return bool(a)
 except Exception as e:p.write_text(json.dumps({'symbol':sym,'error':str(e)}));return False
with concurrent.futures.ThreadPoolExecutor(3) as ex:
 n=0;ok=0
 for b in ex.map(f,pool):
  n+=1;ok+=b
  if n%60==0:print(n,ok,flush=True)
print('done',n,ok,flush=True)
