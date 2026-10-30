import json,pathlib,datetime,re,collections
pool=json.load(open('work/pool.json'));results=[];count=collections.Counter()
def load(p):
 try:return json.load(open(p))
 except:return {}
def num(v):
 try:return float(str(v).replace('$','').replace(',','').replace('(','-').replace(')','').strip())
 except:return None
def finance(s,kind):
 d=load('work/enriched/'+s+'_'+kind+'.json').get('data') or {};t=d.get('incomeStatementTable') or {};r=next((r for r in t.get('rows',[]) if r.get('value1')=='Net Income Applicable to Common Shareholders'),None)
 if not r:return []
 out=[]
 for k,v in t.get('headers',{}).items():
  if k=='value1':continue
  try:date=datetime.datetime.strptime(v,'%m/%d/%Y').date()
  except:continue
  val=num(r.get(k))
  if val is not None:out.append((date,val*1000))
 return sorted(out,reverse=True)
for x in pool:
 s=x['ticker'];price=num(x['price']);q=finance(s,'quarter');annual=finance(s,'annual');pe='缺可用TTM数据';pesrc='';penote=''
 if len(q)==4 and all(70<=(q[i][0]-q[i+1][0]).days<=110 for i in range(3)) and q[0][0]<=datetime.date(2026,10,27) and (datetime.date(2026,10,27)-q[0][0]).days<200:
  total=sum(v for d,v in q)
  pe=round(x['cap']/total,2) if total>0 else ('亏损/不适用' if total<0 else '零利润/不适用')
  pesrc=f'https://api.nasdaq.com/api/company/{s}/financials?frequency=2'
  penote='估算：10/27总市值÷最近四季普通股股东净利润；报告期'+','.join(str(d) for d,v in q)+'；源金额按千美元转换。与稀释EPS口径有差异；10/28取得，未逐份核验披露日及后续重述，非严格PIT。'
  count['pe_calculated']+=1
 if s=='NVDA':
  pe=27.56;pesrc='https://tushare.pro/document/2?doc_id=254';penote='Tushare us_daily，trade_date=20261027，PE=27.56；Finviz稀释TTM EPS=7.91，10/27收盘217.94÷7.91≈27.55作交叉核对。';count['pe_direct']+=1
 # Only dated exact-base CMC history can replace no-data; otherwise keep explicitly approximate snapshot.
 cm=load('work/pe/cmc/'+s+'.json');hist=cm.get('history') or []
 if not isinstance(pe,(int,float)) and pe=='缺可用TTM数据' and hist:
  z=hist[-1];dt=datetime.datetime.fromtimestamp(z['d'],datetime.timezone.utc).date();v=num(z['v'])
  if datetime.date(2026,10,18)<=dt<=datetime.date(2026,10,28) and v is not None and v!=0:
   # current quote price from list lets us normalize a snapshot PE to the common baseline price
   txt=cm.get('text','');m=re.search(r'\$([\d,.]+)\s*Share price',txt,re.I)
   cmprice=num(m.group(1)) if m else None
   if cmprice and cmprice>0:
    pe=round(v*price/cmprice,2) if v>0 else '亏损/不适用'
    pesrc=cm['url'];penote=f'近似：网站TTM PE={v:g}（{dt}），网站股价={cmprice:g}；换算为10/27收盘价{price:g}。利润取网站最新口径，未核验历史披露时点。';count['pe_cmc_rebased']+=1
   elif dt==datetime.date(2026,10,27):
    pe=round(v,2) if v>0 else '亏损/不适用';pesrc=cm['url'];penote='网站TTM历史点日期2026-10-27。';count['pe_cmc_exact']+=1
 if pe=='缺可用TTM数据' and cm.get('text'):
  txt=cm['text'];m=re.search(r'current price-to-earnings ratio \(TTM\) is\s*([\d.,-]+)',txt);pr=re.search(r'\$([\d,.]+)\s*Share price',txt,re.I)
  val=num(m.group(1).rstrip('.')) if m else None;cp=num(pr.group(1)) if pr else None
  if val and cp and cp>0:
   pe=round(val*price/cp,2) if val>0 else '亏损/不适用';pesrc=cm['url'];penote=f'近似：10/28检索页面最新TTM PE={val:g}，页面股价={cp:g}；按10/27收盘价{price:g}换算。页面图表无当日点，利润历史披露时点未核验。';count['pe_cmc_text_rebased']+=1
 if pe=='缺可用TTM数据':
  pesrc=cm.get('url') or f'https://api.nasdaq.com/api/company/{s}/financials?frequency=2'
  penote='已逐家检查；Nasdaq缺足够且连续的近期季度普通股股东利润；'+('公开估值页面请求失败：'+str(cm['error']) if cm.get('error') else '公开估值页面未取得可核对的近期TTM值。未用年度PE或预测PE冒充TTM。')
 vals=[];ends=[];notes=[]
 forecasts=(load('work/enriched/'+s+'_forecast.json').get('data') or {}).get('yearlyForecast') or {}
 fs={}
 for z in forecasts.get('rows') or []:
  try:year=int(z['fiscalEnd'][-4:]);eps=num(z['consensusEPSForecast'])
  except:continue
  if eps is not None:fs[year]=(z['fiscalEnd'],eps,z.get('noOfEstimates'))
 for y in [2025,2026,2027,2028]:
  a=next(((d,v) for d,v in annual if d.year==y and d<=datetime.date(2026,10,27)),None)
  if a:
   d,v=a;vals.append(round(v/1e8,4));ends.append(str(d));notes.append(f'{y}：财报普通股股东净利润实际值');count[str(y)+'_actual']+=1
  elif y in fs:
   end,eps,n=fs[y];val=eps*(x['cap']/price)/1e8
   vals.append(round(val,4));ends.append(end);notes.append(f'{y}：估算EPS={eps:g}×10/27隐含股数，分析师{n}位');count[str(y)+'_estimate']+=1
  else:vals.append('未找到公开年度值/预测');ends.append('未取得');count[str(y)+'_missing']+=1
 note='；'.join(notes)+'。年份按财年截止年，不等同自然年。实际值源表千美元换算亿美元；10/28转载快照未排除后续重述；预测通常为调整后EPS，并非GAAP净利润一致预期，股数固定未考虑未来回购/摊薄；ADR/多类别股可能有口径偏差。预测接口asOf为空，10/28检索快照，不能当作10/27历史共识。'
 sources=f'https://api.nasdaq.com/api/company/{s}/financials?frequency=1 | https://api.nasdaq.com/api/analyst/{s}/earnings-forecast'
 results.append({'ticker':s,'pe':pe,'profits':vals,'extra':[pesrc,penote,sources]+ends+[note]})
pathlib.Path('work/pe/prepared.json').write_text(json.dumps(results,ensure_ascii=False));print(dict(count))
print('numeric PE',sum(isinstance(x['pe'],(int,float)) for x in results),'loss',sum(x['pe']=='亏损/不适用' for x in results))
