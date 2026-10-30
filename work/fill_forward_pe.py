import json,pathlib,math,collections
from feishu_api import connect,api
t,s=connect();base=f'sheets/v2/spreadsheets/{s}'
before=api('GET',base+'/values/K3baGL!A1:BP459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
pathlib.Path('work/before_forward_pe.json').write_text(json.dumps(before,ensure_ascii=False))
headers=['FY2026 PE(市值/利润)','FY2027 PE(市值/利润)','FY2028 PE(市值/利润)','FY2026–2028利润同比均值%']
def formulas(i):
 fs=[]
 for c in ['M','N','O']:
  fs.append(f'=IF(COUNT(F{i},{c}{i})<2,"缺数据",IF({c}{i}<=0,"亏损/零利润不适用",F{i}/{c}{i}))')
 fs.append(f'=IF(COUNT(L{i}:O{i})<4,"缺数据",IF(MIN(L{i}:N{i})<=0,"基期利润非正不适用",AVERAGE(M{i}/L{i}-1,N{i}/M{i}-1,O{i}/N{i}-1)))')
 return [{'type':'formula','text':f} for f in fs]
# Verify formula interpretation on first data row before batching.
api('PUT',base+'/values',t,{'valueRange':{'range':'K3baGL!H2:K2','values':[formulas(2)]}})
sample=api('GET',base+'/values/K3baGL!H2:K2?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values'][0]
assert all(isinstance(v,(int,float)) for v in sample),sample
print('formula sample',sample,flush=True)
values=[headers]+[formulas(i) for i in range(2,460)]
for start in range(0,len(values),100):
 batch=values[start:start+100]
 api('PUT',base+'/values',t,{'valueRange':{'range':f'K3baGL!H{start+1}:K{start+len(batch)}','values':batch}})
api('PUT',base+'/styles_batch_update',t,{'data':[{'ranges':['K3baGL!H2:J459'],'style':{'formatter':'0.00'}},{'ranges':['K3baGL!K2:K459'],'style':{'formatter':'0.00%'}}]})
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
