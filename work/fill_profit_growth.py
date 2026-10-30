import json,pathlib,datetime,math,collections
from feishu_api import connect,api

def prior_profit(symbol):
 try:
  root=json.load(open('work/enriched/'+symbol+'_annual.json'));tab=(root.get('data') or {}).get('incomeStatementTable') or {}
  row=next((r for r in tab.get('rows',[]) if r.get('value1')=='Net Income Applicable to Common Shareholders'),{})
  for k,v in (tab.get('headers') or {}).items():
   if k=='value1':continue
   try:d=datetime.datetime.strptime(v,'%m/%d/%Y').date()
   except:continue
   if d.year!=2024:continue
   try:n=float(str(row.get(k)).replace('$','').replace(',',''))/100000
   except:continue
   return round(n,4),str(d)
 except:pass
 return '未取得FY2024利润','未取得'

t,s=connect();base=f'sheets/v2/spreadsheets/{s}'
before=api('GET',base+'/values/K3baGL!A1:BP459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
oldform=api('GET',base+'/values/K3baGL!H2:K459?valueRenderOption=Formula',t)['data']['valueRange']['values']
assert all(isinstance(v,str) and v.startswith('=') for row in oldform for v in row)
pathlib.Path('work/before_profit_growth.json').write_text(json.dumps(before,ensure_ascii=False))
meta=api('GET',f'sheets/v3/spreadsheets/{s}/sheets/query',t)
sh=next(x for x in meta['data']['sheets'] if x['sheet_id']=='K3baGL');n=sh['grid_properties']['column_count']
if n<72:api('POST',base+'/dimension_range',t,{'dimension':{'sheetId':'K3baGL','majorDimension':'COLUMNS','length':72-n}})
aux=[['FY2024普通股股东净利润(亿美元)','FY2024财年截止日','FY2024利润来源','同比计算口径说明']]
form=[['FY2025净利润同比%','FY2026净利润同比%','FY2027净利润同比%','FY2028净利润同比%']]
for i,row in enumerate(before[1:],2):
 sym=row[3];profit,date=prior_profit(sym)
 aux.append([profit,date,f'https://api.nasdaq.com/api/company/{sym}/financials?frequency=1','年份按财年截止年；2024基数为Nasdaq普通股股东净利润，源表千美元换算亿美元。同比=(本年/上年)-1；基期≤0不计算常规增速。L–O可能混有实际及调整后EPS估算利润，跨口径同比仅供参考。'])
 out=[]
 for curr,prev in [('L','BQ'),('M','L'),('N','M'),('O','N')]:
  f=f'=IF(COUNT({curr}{i},{prev}{i})<2,"缺数据",IF({prev}{i}<=0,"基期利润非正不适用",{curr}{i}/{prev}{i}-1))'
  out.append({'type':'formula','text':f})
 form.append(out)
for left,right,values in [('BQ','BT',aux),('S','V',form)]:
 for start in range(0,len(values),100):
  batch=values[start:start+100]
  api('PUT',base+'/values',t,{'valueRange':{'range':f'K3baGL!{left}{start+1}:{right}{start+len(batch)}','values':batch}})
 print('written',left,right,flush=True)
api('PUT',base+'/styles_batch_update',t,{'data':[{'ranges':['K3baGL!S2:V459'],'style':{'formatter':'0.00%'}},{'ranges':['K3baGL!BQ2:BQ459'],'style':{'formatter':'#,##0.00'}}]})
after=api('GET',base+'/values/K3baGL!A1:BT459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
newform=api('GET',base+'/values/K3baGL!H2:K459?valueRenderOption=Formula',t)['data']['valueRange']['values'];assert oldform==newform
svform=api('GET',base+'/values/K3baGL!S2:V459?valueRenderOption=Formula',t)['data']['valueRange']['values']
assert svform==[[cell['text'] for cell in row] for row in form[1:]]
counts=collections.Counter()
for i,(a,b) in enumerate(zip(before[1:],after[1:]),1):
 assert a[:18]==b[:18] and a[22:]==b[22:68],i
 vals=[a[11],a[12],a[13],a[14]];prev=[aux[i][0],a[11],a[12],a[13]]
 for c,x,y,z in zip('STUV',vals,prev,b[18:22]):
  if not isinstance(x,(int,float)) or not isinstance(y,(int,float)):expected='缺数据'
  elif y<=0:expected='基期利润非正不适用'
  else:expected=x/y-1
  if isinstance(expected,(int,float)):
   assert isinstance(z,(int,float)) and math.isclose(expected,z,rel_tol=1e-9,abs_tol=1e-10),(i,c,expected,z)
   counts[c+'_numeric']+=1
  else:
   assert expected==z,(i,c,expected,z);counts[c+'_'+expected]+=1
print('VERIFIED',dict(counts),flush=True)
pathlib.Path('work/profit_growth_verified.json').write_text(json.dumps(dict(counts),ensure_ascii=False))
