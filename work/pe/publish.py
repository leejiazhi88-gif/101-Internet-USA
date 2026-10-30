import json,sys,pathlib
sys.path.insert(0,'work')
from feishu_api import connect,api
r={x['ticker']:x for x in json.load(open('work/pe/prepared.json'))}
t,s=connect();base=f'sheets/v2/spreadsheets/{s}'
current=api('GET',base+'/values/K3baGL!A1:BH459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
bk=pathlib.Path('work/pe/before.json')
if not bk.exists():bk.write_text(json.dumps(current,ensure_ascii=False))
assert len(current)==459
codes=[row[3] for row in current[1:]];assert len(set(codes))==458 and set(codes)==set(r)
meta=api('GET',f'sheets/v3/spreadsheets/{s}/sheets/query',t);sheet=next(x for x in meta['data']['sheets'] if x['sheet_id']=='K3baGL');n=sheet['grid_properties']['column_count']
if n<68:api('POST',base+'/dimension_range',t,{'dimension':{'sheetId':'K3baGL','majorDimension':'COLUMNS','length':68-n}})
pe=[['PE(TTM)']]+[[r[c]['pe']] for c in codes]
profits=[['FY2025净利润(实际/估算,亿美元)','FY2026净利润(实际/估算,亿美元)','FY2027净利润(估算,亿美元)','FY2028净利润(估算,亿美元)']]+[r[c]['profits'] for c in codes]
extra=[['PE来源','PE口径与日期备注','利润来源','FY2025截止日','FY2026截止日','FY2027截止日','FY2028截止日','利润口径备注']]+[r[c]['extra'] for c in codes]
for a,b,values in [('G','G',pe),('L','O',profits),('BI','BP',extra)]:
 for start in range(0,len(values),100):
  batch=values[start:start+100];address=f'K3baGL!{a}{start+1}:{b}{start+len(batch)}'
  api('PUT',base+'/values',t,{'valueRange':{'range':address,'values':batch}})
 actual=api('GET',base+f'/values/K3baGL!{a}1:{b}459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
 def pad(x):
  x=[''.join(z.get('text','') for z in v) if isinstance(v,list) else ('' if v is None else v) for v in x]
  return x+['']*(len(values[0])-len(x))
 assert [pad(x) for x in actual]==values,a
 print('written and verified',a,b,flush=True)
p= f'sheets/v3/spreadsheets/{s}/sheets/K3baGL/filter'
f=api('GET',p,t)['data']['sheet_filter_info']
if not f.get('filter_infos') and not f.get('filtered_out_rows') and f.get('range')!='K3baGL!A1:BP459':
 api('DELETE',p,t);api('POST',p,t,{'range':'K3baGL!A1:BP459','col':'A','condition':{'filter_type':'clear'}})
pathlib.Path('work/pe/published.json').write_text(json.dumps({'companies':len(codes),'numeric_pe':sum(isinstance(r[c]['pe'],(int,float)) for c in codes),'pe_loss':sum(r[c]['pe']=='亏损/不适用' for c in codes),'profits':[sum(isinstance(r[c]['profits'][i],(int,float)) for c in codes) for i in range(4)]}))
