import json,sys,re
sys.path.insert(0,'work');from feishu_api import connect,api
def norm(v):
    if isinstance(v,list):return ''.join(str(x.get('text','')) if isinstance(x,dict) else str(x) for x in v)
    return v
def colnum(s):
    n=0
    for ch in s:n=n*26+ord(ch)-64
    return n
T,S=connect();base=f'sheets/v2/spreadsheets/{S}'
live=api('GET',base+'/values/K3baGL!A1:BT500?valueRenderOption=UnformattedValue',T)['data']['valueRange']['values']
rows={norm(r[3]):(i+1,r) for i,r in enumerate(live[1:],1) if len(r)>3 and norm(r[3])}
writes=[];red=[]
def add(cell,val):
    writes.append((cell,val));red.append(f'K3baGL!{cell}:{cell}')
def append(old,new):
    old=norm(old)
    if not old:return new
    if new in old:return old
    return old+'\n'+new

income=json.load(open('work/special_income_candidates.json'))
unfilled={(x['ticker'],x['column']):x for x in income['unfilled']}
fx=json.load(open('work/special_fx_candidates.json'))['candidates']
for x in fx:
    s=x['ticker'];row,r=rows[s];c=x['column'];orig=unfilled.get((s,c))
    source=x['source'] if not orig else orig['source']+' | '+x['source']
    src_col={'L':'AS','AY':'BA'}[c];note_col={'L':'AX','AY':'BB'}[c]
    add(f'{src_col}{row}',append(r[colnum(src_col)-1],source))
    add(f'{note_col}{row}',append(r[colnum(note_col)-1],x['note']))
    if c=='AY':
        add(f'BS{row}',append(r[70],source));add(f'BT{row}',append(r[71],x['note']))
for x in income['candidates']:
    s=x['ticker'];row,r=rows[s];c=x['column'];src_col={'L':'AS','AY':'BA'}[c];note_col={'L':'AX','AY':'BB'}[c]
    add(f'{src_col}{row}',append(r[colnum(src_col)-1],x['source']))
    add(f'{note_col}{row}',append(r[colnum(note_col)-1],x['note']))
for x in json.load(open('work/special_profit_candidates.json')):
    if not x.get('verified'):continue
    s=x['ticker'];row,r=rows[s];add(f'AS{row}',append(r[44],x['source']));add(f'AX{row}',append(r[49],x['note']))
for x in json.load(open('work/special_extra_forecast.json')):
    if not x.get('verified') or x.get('netincome') is None:continue
    s=x['ticker'];row,r=rows[s];add(f'AS{row}',append(r[44],x['source']));add(f'AX{row}',append(r[49],x['notedata']))

comp=json.load(open('work/special_composition_candidates.json'))
for s in {x['ticker'] for x in comp['candidates']}:
    row,r=rows[s];xs=[x for x in comp['candidates'] if x['ticker']==s]
    sources=' | '.join(dict.fromkeys(x['source'] for x in xs));notes='\n'.join(dict.fromkeys(x['note'] for x in xs))
    add(f'BC{row}',append(r[54],sources));add(f'BD{row}',append(r[55],notes))

for cell,val in writes:
    api('PUT',base+'/values',T,{'valueRange':{'range':f'K3baGL!{cell}:{cell}','values':[[val]]}})
for i in range(0,len(red),80):
    api('PUT',base+'/styles_batch_update',T,{'data':[{'ranges':red[i:i+80],'style':{'foreColor':'#C00000'}}]})
print('fixed cumulative source/note cells',len(writes),flush=True)
after=api('GET',base+'/values/K3baGL!A1:BT500?valueRenderOption=UnformattedValue',T)['data']['valueRange']['values']
for cell,val in {c:v for c,v in writes}.items():
    m=re.match(r'([A-Z]+)(\d+)',cell);got=norm(after[int(m.group(2))-1][colnum(m.group(1))-1]);assert got==val,(cell,got,val)
print('verified',flush=True)
