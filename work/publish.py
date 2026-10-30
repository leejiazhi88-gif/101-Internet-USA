import json,pathlib,collections
from feishu_api import connect,api
rows=json.load(open('work/prepared_values.json'))
t,ss=connect()
meta=api('GET',f'sheets/v3/spreadsheets/{ss}/sheets/query',t)
sheet=next(s for s in meta['data']['sheets'] if s['sheet_id']=='K3baGL')
print('target',sheet['sheet_id'],sheet['title'],flush=True)
backup=api('GET',f'sheets/v2/spreadsheets/{ss}/values/K3baGL!A1:BC203',t)
pathlib.Path('work/before_publish.json').write_text(json.dumps(backup,ensure_ascii=False))
for major,current,target in [('ROWS',sheet['grid_properties']['row_count'],500),('COLUMNS',sheet['grid_properties']['column_count'],60)]:
 if current<target:
  print(api('POST',f'sheets/v2/spreadsheets/{ss}/dimension_range',t,{'dimension':{'sheetId':'K3baGL','majorDimension':major,'length':target-current}}),flush=True)
for start in range(0,len(rows),80):
 batch=rows[start:start+80]
 api('PUT',f'sheets/v2/spreadsheets/{ss}/values',t,{'valueRange':{'range':f'K3baGL!A{start+1}:BH{start+len(batch)}','values':batch}})
 print('written',start+1,start+len(batch),flush=True)
after=api('GET',f'sheets/v2/spreadsheets/{ss}/values/K3baGL!A1:BH{len(rows)}?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
assert len(after)==len(rows),(len(after),len(rows))
for i,(a,b) in enumerate(zip(rows,after)):
 assert a==b,(i+1,[(j,x,y) for j,(x,y) in enumerate(zip(a,b)) if x!=y][:3])
pathlib.Path('work/publish_verified.json').write_text(json.dumps({'rows':len(rows)-1,'columns':60,'verified':True},ensure_ascii=False))
print('READBACK VERIFIED',len(rows)-1,flush=True)
