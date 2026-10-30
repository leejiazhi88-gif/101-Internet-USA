"""Apply explicitly sourced fallback values and mark those cells red."""
import json, pathlib, sys
sys.path.insert(0,'work')
from feishu_api import connect, api

def norm(v):
    if isinstance(v,list):
        return ''.join(str(x.get('text','')) if isinstance(x,dict) else str(x) for x in v)
    return v

def colnum(s):
    n=0
    for ch in s:
        n=n*26+ord(ch)-64
    return n

token, ss = connect(); base=f'sheets/v2/spreadsheets/{ss}'
def get(rng, option='Formula'):
    return api('GET',base+f'/values/K3baGL!{rng}?valueRenderOption={option}',token)['data']['valueRange']['values']
live=get('A1:BT500','Formula')
pathlib.Path('work/special_apply_before.json').write_text(json.dumps(live,ensure_ascii=False))
assert live[0][33:37]==['25年收入构成','25年利润构成','26年收入构成','26年利润构成']
rows={norm(r[3]):(i+1,r) for i,r in enumerate(live[1:],1) if len(r)>3 and norm(r[3])}
assert len(rows)==458

writes=[];red=[];touched_profit=set();touched_history=set();touched_composition=set()
def put_cell(cell,val): writes.append((cell,val))
def red_cell(cell): red.append(f'K3baGL!{cell}:{cell}')
def append(old,new):
    old=norm(old)
    if not old:return new
    if new in old:return old
    return old+'\n'+new
def setrow(row, col, val, mark=True):
    put_cell(f'{col}{row}',val)
    if mark:red_cell(f'{col}{row}')

# PE fallbacks. Existing 10/28 rebased/near-date PE values are also special.
pe=json.load(open('work/special_pe_candidates.json'))
for s,(row,r) in rows.items():
    ar=norm(r[43])
    if any(k in ar for k in ['近似：','10/28检索页面最新','网站TTM PE=','近似补缺']): red_cell(f'G{row}')
for x in pe:
    s=x['ticker']; row,r=rows[s]; value=x.get('value')
    if value is None:value=x.get('suggested_display') or ('亏损/不适用' if x.get('loss_status_verified') else '缺可用TTM数据')
    setrow(row,'G',value)
    setrow(row,'AQ',x['source'])
    note=x['notes']+('；页面同时显示近12个月净亏损，PE不适用。' if x.get('loss_status_verified') else '')
    setrow(row,'AR',note)

# Historical fallback cells and three corrected 2026-10-27 baseline closes.
hist=json.load(open('work/special_history_candidates.json'))
for x in hist['candidates']:
    s=x['ticker'];row,r=rows[s];setrow(row,x['column'],x['value']);touched_history.add(row)
for s,close in {'PLTR':198.73,'COIN':161.09,'BRK.B':542.99}.items():
    row,r=rows[s];setrow(row,'AO',close);touched_history.add(row)
    note=hist['warnings'].get(s,'') if isinstance(hist.get('warnings'),dict) else ''
    if not note:note=f'补采历史行情后发现：2026-10-27同源收盘价为{close}美元；原基准收盘价已更正。'
    setrow(row,'AP',append(r[41],note))

# Profit actuals recovered from nearby/current public financial snapshots.
special_profit_rows=set();special_ay_rows=set()
income=json.load(open('work/special_income_candidates.json'))['candidates']
fx=json.load(open('work/special_fx_candidates.json'))['candidates']
for x in income:
    s=x['ticker'];row,r=rows[s];c=x['column'];setrow(row,c,x['value']);touched_profit.add(row);special_profit_rows.add(row)
    datecol={'L':'AT','AY':'AZ'}[c];setrow(row,datecol,x['fiscal_end'])
    sourcecol={'L':'AS','AY':'BA'}[c];setrow(row,sourcecol,x['source'])
    notecol={'L':'AX','AY':'BB'}[c];setrow(row,notecol,append(r[{'AX':49,'BB':53}[notecol]],x['note']))
    if c=='AY':special_ay_rows.add(row)
for x in fx:
    s=x['ticker'];row,r=rows[s];c=x['column'];setrow(row,c,x['value']);touched_profit.add(row);special_profit_rows.add(row)
    setrow(row,{'L':'AT','AY':'AZ'}[c],x['period_end'])
    setrow(row,{'L':'AS','AY':'BA'}[c],x['source'])
    setrow(row,{'L':'AX','AY':'BB'}[c],append(r[{'AX':49,'BB':53}[{'L':'AX','AY':'BB'}[c]]],x['note']))
    if c=='AY':
        special_ay_rows.add(row)
        # BQ:BT are supporting FY2024 inputs used by the visible S formula.
        setrow(row,'BQ',x['value']);setrow(row,'BR',x['period_end']);setrow(row,'BS',x['source']);setrow(row,'BT',x['note'])

# Direct annual/forecast estimates (only verified entries).
forecasts=json.load(open('work/special_profit_candidates.json'))
for x in forecasts:
    if not x.get('verified'):continue
    s=x['ticker'];row,r=rows[s];c=x['column'];setrow(row,c,x['value']);touched_profit.add(row);special_profit_rows.add(row)
    setrow(row,{'M':'AU','N':'AV','O':'AW'}[c],x['fiscal_end'])
    setrow(row,'AS',x['source']);setrow(row,'AX',append(r[49],x['note']))
for x in json.load(open('work/special_extra_forecast.json')):
    if not x.get('verified') or x.get('netincome') is None:continue
    s=x['ticker'];row,r=rows[s];c={2026:'M',2027:'N',2028:'O'}[x['year']]
    setrow(row,c,round(x['netincome']/1e8,4));touched_profit.add(row);special_profit_rows.add(row)
    setrow(row,{'M':'AU','N':'AV','O':'AW'}[c],f'{x["year"]}-12-31')
    setrow(row,'AS',x['source']);setrow(row,'AX',append(r[49],x['notedata']))

# Composition recoveries and official proof that SKHY split profit is unavailable.
comp=json.load(open('work/special_composition_candidates.json'))
for x in comp['candidates']:
    s=x['ticker'];row,r=rows[s];c=x['column'];setrow(row,c,x['value']);touched_composition.add(row)
    setrow(row,'BC',x['source']);setrow(row,'BD',append(r[55],x['note']))
for x in comp.get('missing',[]):
    s=x['ticker'];row,r=rows[s];c=x['column'];setrow(row,c,x['note']);touched_composition.add(row)
    setrow(row,'BC',x['source']);setrow(row,'BD',append(r[55],x['note']))

# Mark formulas that depend on special profit inputs too.
for row in special_profit_rows:
    for c in ['H','I','J','K','S','T','U','V']:red_cell(f'{c}{row}')
for row in special_ay_rows:red_cell(f'S{row}')

for cell,val in writes:
    api('PUT',base+'/values',token,{'valueRange':{'range':f'K3baGL!{cell}:{cell}','values':[[val]]}})
print('value writes',len(writes),flush=True)
for start in range(0,len(red),80):
    api('PUT',base+'/styles_batch_update',token,{'data':[{'ranges':red[start:start+80],'style':{'foreColor':'#C00000'}}]})
print('red cells',len(set(red)),flush=True)

after=get('A1:BT500','Formula')
def cellv(a,cell):
    import re
    m=re.match(r'([A-Z]+)(\d+)',cell);return norm(a[int(m.group(2))-1][colnum(m.group(1))-1])
oldform={(row,c):norm(live[row-1][colnum(c)-1]) for row in range(2,460) for c in ['H','I','J','K','S','T','U','V']}
newform={(row,c):norm(after[row-1][colnum(c)-1]) for row in range(2,460) for c in ['H','I','J','K','S','T','U','V']}
assert oldform==newform,'formula cells changed'
final_expected={cell:val for cell,val in writes}
for cell,val in final_expected.items(): assert cellv(after,cell)==val,(cell,cellv(after,cell),val)
pathlib.Path('work/special_apply_after.json').write_text(json.dumps(after,ensure_ascii=False))
print('VERIFIED',len(writes),'value writes; formulas preserved; red style batches applied.',flush=True)
