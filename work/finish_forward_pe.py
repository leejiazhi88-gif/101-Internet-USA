import json,pathlib,math,collections
from feishu_api import connect,api
t,s=connect();base=f'sheets/v2/spreadsheets/{s}'
before=json.load(open('work/before_forward_pe.json'))
api('PUT',base+'/styles_batch_update',t,{'data':[{'ranges':['K3baGL!H2:J459'],'style':{'formatter':'#,##0.00'}},{'ranges':['K3baGL!K2:K459'],'style':{'formatter':'0.00%'}}]})
after=api('GET',base+'/values/K3baGL!A1:BP459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
counts=collections.Counter()
for idx,(a,b) in enumerate(zip(before[1:],after[1:]),2):
 assert a[:7]==b[:7] and a[11:]==b[11:],idx
 f=a[5];profits=a[11:15];expected=[]
 for p in profits[1:]:
  if not isinstance(f,(int,float)) or not isinstance(p,(int,float)):v='缺数据'
  elif p<=0:v='亏损/零利润不适用'
  else:v=f/p
  expected.append(v)
 if not all(isinstance(x,(int,float)) for x in profits):v='缺数据'
 elif min(profits[:3])<=0:v='基期利润非正不适用'
 else:v=sum(profits[j+1]/profits[j]-1 for j in range(3))/3
 expected.append(v)
 for c,e,z in zip('HIJK',expected,b[7:11]):
  if isinstance(e,(int,float)):
   assert isinstance(z,(int,float)) and math.isclose(e,z,rel_tol=1e-9,abs_tol=1e-10),(idx,c,e,z)
   counts[c+'_numeric']+=1
  else:assert e==z,(idx,c,e,z)
print('VERIFIED',dict(counts),flush=True)
pathlib.Path('work/forward_pe_verified.json').write_text(json.dumps(dict(counts)))
