import json,pathlib,collections,colorsys
from feishu_api import connect,api
t,s=connect();base=f'sheets/v2/spreadsheets/{s}';address='K3baGL!A1:E459'
values=api('GET',base+'/values/'+address+'?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
assert values[0][2]=='目录二级'
cf=api('GET',base+'/condition_formats?sheet_ids=K3baGL',t)
groups=collections.OrderedDict()
for i,row in enumerate(values[1:],2):
 if row and row[0]:groups.setdefault(row[2],[]).append(i)
styles=[];mapping={}
for j,(group,indices) in enumerate(groups.items()):
 hue=(j*0.38196601125)%1
 rgb=colorsys.hls_to_rgb(hue,0.88 if j%2==0 else 0.93,0.65)
 color='#'+''.join(f'{round(v*255):02X}' for v in rgb);mapping[group]=color
 runs=[];start=last=indices[0]
 for i in indices[1:]:
  if i!=last+1:runs.append((start,last));start=i
  last=i
 runs.append((start,last))
 styles.append({'ranges':[f'K3baGL!A{a}:E{b}' for a,b in runs],'style':{'backColor':color}})
print(api('PUT',base+'/styles_batch_update',t,{'data':styles}))
assert values==api('GET',base+'/values/'+address+'?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values']
assert cf==api('GET',base+'/condition_formats?sheet_ids=K3baGL',t)
pathlib.Path('work/gics_group_colors.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
print('Colored',len(groups),'groups;',sum(map(len,groups.values())),'companies; values and conditional formats unchanged.')
