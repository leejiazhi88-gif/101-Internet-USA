import json,pathlib,re,collections
from feishu_api import connect,api
entries={}
for line in pathlib.Path('work/company_zh.tsv').read_text().splitlines():
 s,cn,desc=line.split('\t');assert s not in entries;assert re.search('[\u4e00-\u9fff]',cn);assert not desc.startswith('行业');entries[s]={'cn':cn,'description':desc,'profile_source':f'https://api.nasdaq.com/api/company/{s}/company-profile'}
assert len(entries)==458
assert len({v['description'] for v in entries.values()})==458
pool={x['ticker']:x for x in json.load(open('work/pool.json'))}
t,ss=connect();base=f'sheets/v2/spreadsheets/{ss}'
original=api('GET',base+'/values/K3baGL!A1:BP459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
assert len(original)==459 and original[0][3]=='代码'
pathlib.Path('work/before_company_zh.json').write_text(json.dumps(original,ensure_ascii=False))
codes=[r[3] for r in original[1:]];assert len(set(codes))==458 and set(codes)==set(entries)
cf=api('GET',base+'/condition_formats?sheet_ids=K3baGL',t)
valuesA=[[entries[s]['cn']+' '+pool[s]['name']] for s in codes]
valuesE=[[entries[s]['description']] for s in codes]
for col,values in [('A',valuesA),('E',valuesE)]:
 for start in range(0,len(values),100):
  batch=values[start:start+100]
  api('PUT',base+'/values',t,{'valueRange':{'range':f'K3baGL!{col}{start+2}:{col}{start+len(batch)+1}','values':batch}})
 print('written',col,len(values),flush=True)
api('PUT',base+'/styles_batch_update',t,{'data':[{'ranges':['K3baGL!E2:E459'],'style':{'wordWrap':True}}]})
after=api('GET',base+'/values/K3baGL!A1:BP459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
assert original[0]==after[0]
for i,(old,new) in enumerate(zip(original[1:],after[1:])):
 assert new[0]==valuesA[i][0] and new[4]==valuesE[i][0],i
 assert old[1:4]==new[1:4] and old[5:]==new[5:],i
assert cf==api('GET',base+'/condition_formats?sheet_ids=K3baGL',t)
pathlib.Path('work/company_zh_audit.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2))
print('VERIFIED: 458 bilingual names, 458 distinct Chinese descriptions. Other values and conditional formats unchanged.',flush=True)
