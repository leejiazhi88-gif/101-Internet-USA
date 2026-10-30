import json,pathlib,math
from feishu_api import connect,api
t,s=connect();base=f'sheets/v2/spreadsheets/{s}';address='K3baGL!X2:AG459'
before=api('GET',base+'/values/'+address+'?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
pathlib.Path('work/returns_before_percent.json').write_text(json.dumps(before))
values=[[v/100 if isinstance(v,(int,float)) else v for v in row] for row in before]
api('PUT',base+'/values',t,{'valueRange':{'range':address,'values':values}})
api('PUT',base+'/styles_batch_update',t,{'data':[{'ranges':['K3baGL!X2:AG500'],'style':{'formatter':'0.00%'}}]})
after=api('GET',base+'/values/'+address+'?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
for a,b in zip(values,after):
 for x,y in zip(a,b):
  assert math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12) if isinstance(x,(int,float)) else x==y
shown=api('GET',base+'/values/K3baGL!X2:AG3?valueRenderOption=FormattedValue',t)['data']['valueRange']['values']
print('formatted sample',shown)
assert all(str(v).endswith('%') for row in shown for v in row)
print('Verified percent display and underlying numeric values.')
