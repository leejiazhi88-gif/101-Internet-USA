import pathlib,json,re,html,urllib.request,ssl,concurrent.futures,time
root=pathlib.Path('work/pe/finviz');root.mkdir(exist_ok=True)
pool=json.load(open('work/pool.json'))
def parse(s):
 cells=re.findall(r'<td\b[^>]*>(.*?)</td>',s,re.S)
 cells=[html.unescape(re.sub('<[^>]+>',' ',x)).strip() for x in cells]
 out={}
 for i,v in enumerate(cells[:-1]):
  if v in ['P/E','EPS (ttm)','Income','Earnings','Market Cap','Price','Shs Outstand','Forward P/E']:out[v]=cells[i+1]
 return out

def f(x):
 symbol=x['ticker'];p=root/(symbol+'.json')
 if p.exists():return bool(json.loads(p.read_text()).get('values'))
 try:
  url='https://finviz.com/quote.ashx?t='+symbol.replace('.','-')+'&p=d'
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  raw=urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=20).read().decode()
  vals=parse(raw)
  result={'symbol':symbol,'url':url,'retrieved':'2026-10-28','values':vals,'ttm_label_verified':'Diluted EPS (ttm)' in raw,'page_dates':re.findall(r'Oct (?:27|28).*?ET',raw)[:2]}
  p.write_text(json.dumps(result,ensure_ascii=False))
  time.sleep(.6)
  return bool(vals)
 except Exception as e:
  p.write_text(json.dumps({'symbol':symbol,'error':str(e)}));return False
n=0;ok=0
with concurrent.futures.ThreadPoolExecutor(4) as ex:
 for good in ex.map(f,pool):
  n+=1;ok+=good
  if n%40==0:print(n,ok,flush=True)
print('FINISHED',n,ok,flush=True)
