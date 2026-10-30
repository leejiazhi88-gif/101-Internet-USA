import sys,json,pathlib
sys.path.insert(0,'work')
from feishu_api import connect,api

t,s=connect(); base=f'sheets/v2/spreadsheets/{s}'
# User requested row 204 onward; Feishu dimension indexes are zero-based.
body={
  'dimension': {
    'sheetId': 'K3baGL',
    'majorDimension': 'ROWS',
    'startIndex': 203,
    'endIndex': 500,
  },
  'dimensionProperties': {
    'fixedSize': 21,
  },
}
result=api('PUT',base+'/dimension_range',t,body)
pathlib.Path('work/fix_row_heights_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
