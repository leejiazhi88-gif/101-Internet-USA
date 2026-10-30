import sys,json
sys.path.insert(0,'work')
from feishu_api import connect,api

t,s=connect(); base=f'sheets/v2/spreadsheets/{s}'
paths=[
 base+'/styles_batch_get?ranges=K3baGL!A1:A5',
 base+'/styles?range=K3baGL!A1:A5',
 base+'/style?range=K3baGL!A1:A5',
 base+'/dimension_range?range=K3baGL!A1:A5',
 base+'/dimension_range?sheet_id=K3baGL&major_dimension=ROWS&start_index=0&end_index=5',
]
for p in paths:
 try:
  x=api('GET',p,t); print('OK',p,json.dumps(x,ensure_ascii=False)[:4000])
 except Exception as e: print('ERR',p,repr(e))
