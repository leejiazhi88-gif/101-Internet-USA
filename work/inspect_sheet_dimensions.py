import sys,json,pathlib
sys.path.insert(0,'work')
from feishu_api import connect,api

t,s=connect(); base=f'sheets/v2/spreadsheets/{s}'
meta=api('GET',f'sheets/v3/spreadsheets/{s}/sheets/query',t)
print(json.dumps(meta,ensure_ascii=False,indent=2)[:12000])
for path in [
    base+'/dimension_range?sheetId=K3baGL&majorDimension=ROWS&startIndex=0&endIndex=5',
    base+'/dimension_range?range=K3baGL!A1:A5',
    f'sheets/v3/spreadsheets/{s}/sheets/K3baGL',
]:
    try:
        r=api('GET',path,t)
        print('PATH',path,'\n',json.dumps(r,ensure_ascii=False,indent=2)[:5000])
    except Exception as e:
        print('PATH',path,'ERROR',repr(e))
