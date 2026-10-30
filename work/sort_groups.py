import json,pathlib,re,collections,math
from feishu_api import connect,api

def norm(v):
 if isinstance(v,list):return ''.join(x.get('text','') for x in v)
 return '' if v is None else v

def cells(rows):
 out=[[norm(v) for v in r]+['']*(72-len(r)) for r in rows]
 while out and not any(v!='' for v in out[-1]):out.pop()
 return out

def shift_formula(f,old,new):
 parts=re.split(r'("(?:[^"]|"")*")',f)
 def change(m):
  col,absolute,row=m.groups()
  if absolute:return m.group(0)
  assert int(row)==old,('unexpected cross-row formula',f,old)
  return col+str(new)
 for i in range(0,len(parts),2):parts[i]=re.sub(r'(?<![A-Za-z0-9_])([$]?[A-Z]{1,3})([$]?)([1-9][0-9]*)\b',change,parts[i])
 return ''.join(parts)

t,s=connect();base=f'sheets/v2/spreadsheets/{s}'
raw=api('GET',base+'/values/K3baGL!A1:BT500?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
formsraw=api('GET',base+'/values/K3baGL!A1:BT500?valueRenderOption=Formula',t)['data']['valueRange']['values']
pathlib.Path('work/before_group_sort.json').write_text(json.dumps({'values':raw,'formulas':formsraw},ensure_ascii=False))
values=cells(raw);forms=cells(formsraw)
assert len(values)==459 and len(forms)==459
assert len({r[3] for r in values[1:]})==458
cf=api('GET',base+'/condition_formats?sheet_ids=K3baGL',t)
l1=collections.defaultdict(float);l2=collections.defaultdict(float)
for row in values[1:]:
 assert isinstance(row[5],(float,int)) and row[5]>0
 l1[row[1]]+=row[5];l2[(row[1],row[2])]+=row[5]
order=sorted(range(1,len(values)),key=lambda i:(-l1[values[i][1]],values[i][1],-l2[(values[i][1],values[i][2])],values[i][2],-values[i][5],values[i][3]))
output=[];formula_expected={};expected_values=[]
for target,idx in enumerate(order,2):
 row=[]
 for col,v in enumerate(forms[idx]):
  if isinstance(v,str) and v.startswith('='):
   f=shift_formula(v,idx+1,target);row.append({'type':'formula','text':f});formula_expected[(target,col)]=f
  else:row.append(v)
 output.append(row);expected_values.append(values[idx])
# Record computed order and totals before publication.
pathlib.Path('work/group_sort_plan.json').write_text(json.dumps({'level1':dict(sorted(l1.items(),key=lambda x:-x[1])),'level2':{' / '.join(k):v for k,v in l2.items()},'symbols':[r[3] for r in expected_values]},ensure_ascii=False,indent=2))
# Re-read to avoid overwriting concurrent edits.
assert forms==cells(api('GET',base+'/values/K3baGL!A1:BT500?valueRenderOption=Formula',t)['data']['valueRange']['values'])
for start in range(0,len(output),70):
 batch=output[start:start+70]
 api('PUT',base+'/values',t,{'valueRange':{'range':f'K3baGL!A{start+2}:BT{start+len(batch)+1}','values':batch}})
 print('sorted rows',start+2,start+len(batch)+1,flush=True)
colors=json.load(open('work/gics_group_colors.json'));ranges=collections.defaultdict(list)
start=2;current=expected_values[0][2]
for rownum,row in enumerate(expected_values[1:],3):
 if row[2]!=current:
  ranges[current].append(f'K3baGL!A{start}:E{rownum-1}');start=rownum;current=row[2]
ranges[current].append(f'K3baGL!A{start}:E459')
api('PUT',base+'/styles_batch_update',t,{'data':[{'ranges':rs,'style':{'backColor':colors[g]}} for g,rs in ranges.items()]})
after=cells(api('GET',base+'/values/K3baGL!A1:BT459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values'])
afterforms=cells(api('GET',base+'/values/K3baGL!A1:BT459?valueRenderOption=Formula',t)['data']['valueRange']['values'])
assert after[0]==values[0]
for i,(want,got) in enumerate(zip(expected_values,after[1:]),2):
 for j,(a,b) in enumerate(zip(want,got)):
  if isinstance(a,(int,float)):
   assert isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-10),(i,j,a,b)
  else:assert a==b,(i,j,a,b)
for (i,c),f in formula_expected.items():assert afterforms[i-1][c]==f,(i,c)
assert cf==api('GET',base+'/condition_formats?sheet_ids=K3baGL',t)
print('VERIFIED',len(output),'companies;',len(l1),'level1;',len(l2),'level2;',len(formula_expected),'formulas preserved')
print('level1 order',list(dict(sorted(l1.items(),key=lambda x:-x[1]))))
