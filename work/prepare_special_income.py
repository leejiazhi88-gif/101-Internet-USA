import json,pathlib,sys
sys.path.insert(0,'work/composition')
from parse import obj
rows={r[3]:r for r in json.load(open('work/special_live_before.json'))['data']['valueRange']['values'][1:] if r[3]}
out=[];unfilled=[]
for p in pathlib.Path('work/special_profit').glob('*_income.html'):
 s=p.stem.removesuffix('_income');raw=p.read_text();section=obj(raw,'sections:[');details=obj(raw,'details:')
 assert section['id']=='revenue-income'
 d=section['data'];currency=details['currency'];r=rows[s]
 for year,col,index in [(2025,'L',11),(2024,'AY',50)]:
  if isinstance(r[index],(int,float)):continue
  matches=[(dt,i) for i,dt in enumerate(d.get('datekey',[])) if dt.startswith(str(year)+'-')]
  if not matches:continue
  dt,i=next(((dt,i) for dt,i in matches if s=='FERG' and year==2025 and dt=='2025-07-31'),max(matches))
  n=d.get('netinccmn',[])[i]
  if not isinstance(n,(int,float)):continue
  if currency!='USD':
   unfilled.append({'ticker':s,'column':col,'currency':currency,'date':dt,'net_income':n,'source':f'https://stockanalysis.com/stocks/{s.lower()}/financials/','reason':'需可靠汇率换为亿美元'})
   continue
  note=f'{col}：2026-10-28补采StockAnalysis/S&P公开利润表；年度截至{dt}，归属普通股股东净利润原值{n:g}美元，换算{n/1e8:.4f}亿美元。财报原始披露时间未逐一核验，采用转载页当前快照，不是10/27锁定历史版本。'
  if s=='FERG':note+='采用截至2025-07-31的完整FY2025年度，与2024-07-31前期年度对应；页面另列2025-12-31值，本次不将财年变更期混作该完整年度。'
  if s=='HSBC':note+='本期为S&P归普通股股东口径，表内AY前期Nasdaq值249.99亿美元与S&P同年度229.17亿美元不同；S列同比存在口径差异，仅供参考。'
  if s=='HONA':note+='为上市前业务历史/分拆报表，非独立上市满年度。'
  if s=='SPCX':note+='为上市前历史财务数据，非上市满年度。'
  out.append({'ticker':s,'column':col,'value':round(n/1e8,4),'fiscal_end':dt,'source':f'https://stockanalysis.com/stocks/{s.lower()}/financials/','note':note,'verified':True})
pathlib.Path('work/special_income_candidates.json').write_text(json.dumps({'candidates':out,'unfilled':unfilled},ensure_ascii=False,indent=2))
print('income candidates',len(out),'needfx',len(unfilled))
