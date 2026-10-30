import json,sys,pathlib,collections
sys.path.insert(0,'work')
from feishu_api import connect,api

def norm(v):
 if isinstance(v,list):return ''.join(str(z.get('text','')) if isinstance(z,dict) else str(z) for z in v)
 return v

token,ss=connect();base=f'sheets/v2/spreadsheets/{ss}'
def read():
 return api('GET',base+'/values/K3baGL!A1:BJ500?valueRenderOption=Formula',token)['data']['valueRange']['values']
before=read()
pathlib.Path('work/composition/publish_before.json').write_text(json.dumps(before,ensure_ascii=False))
assert before[0][33:37]==['25年收入构成','25年利润构成','26年收入构成','26年利润构成']
assert not any(any(r[54:56]) for r in before)
prepared=json.load(open('work/composition/prepared.json'))
rows=[(i+1,norm(r[3])) for i,r in enumerate(before[1:],1) if r[3]]
assert len(rows)==458 and [r for r,s in rows]==list(range(2,460))
assert all(s in prepared for _,s in rows)
values=[prepared[s]['values'] for _,s in rows]
notes=[]
for _,s in rows:
 z=prepared[s]
 source=z['sources'] or f'https://stockanalysis.com/stocks/{s.lower().replace(".","-")}/financials/metrics/'
 note='来源：StockAnalysis/Fiscal.ai公开分部表；检索日2026-10-28。25年按财年结束于2025年；26年为已取得的2026年最新年度或单季，非全年预测，非统一累计口径。保留原币种，单位为亿。收入与利润可能采用不同分部划分；利润具体口径见单元格。报告期截止不晚于2026-10-27，未逐一核验历史披露时间，不作严格时点回溯。'
 notes.append([source,note])
def put(r,v):
 api('PUT',base+'/values',token,{'valueRange':{'range':'K3baGL!'+r,'values':v}})
for start in range(0,458,80):
 end=min(start+80,458)
 put(f'AH{start+2}:AK{end+1}',values[start:end])
 print('composition rows',start+2,end+1,flush=True)
put('BC1:BD1',[['收入利润构成来源','收入利润构成口径说明']])
for start in range(0,458,80):
 end=min(start+80,458)
 put(f'BC{start+2}:BD{end+1}',notes[start:end])
api('PUT',base+'/styles_batch_update',token,{'data':[{'ranges':['K3baGL!AH2:AK459','K3baGL!BC1:BD459'],'style':{'wordWrap':True}}]})
after=read()
pathlib.Path('work/composition/publish_after.json').write_text(json.dumps(after,ensure_ascii=False))
for i,(row,s) in enumerate(rows):
 assert [norm(v) for v in after[row-1][33:37]]==values[i],('readback',row)
 assert [norm(v) for v in after[row-1][54:56]]==notes[i],('sources',row)
changed=[]
for r,(a,b) in enumerate(zip(before,after)):
 for c in range(62):
  if 33<=c<=36 or 54<=c<=55:continue
  if norm(a[c])!=norm(b[c]):changed.append((r+1,c+1))
assert not changed,changed[:20]
print('VERIFIED: 458 rows, 1832 composition cells, sources and notes; other values/formulas preserved.')
