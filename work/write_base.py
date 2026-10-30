import json,collections,pathlib
from feishu_api import connect,api
pool=json.load(open('work/pool.json'))
h=json.load(open('work/target_before.json'))['data']['valueRange']['values'][0][:55]
h=[str(x or '').replace('亿元','亿美元') for x in h]
h+=['GICS二级代码','GICS分类核验状态','入选依据','基准日收盘价(美元)','数据来源与口径说明']
rows=[h]
for x in pool:
 r=['待核实']*55
 r[:6]=[x['name'],x['sector_cn'],x['group_cn'],x['ticker'],'行业：'+(x['subindustry'] or x['industry_raw']),round(x['cap']/1e8,4)]
 for i in list(range(7,18))+list(range(19,22))+[34,36]+list(range(39,47)):
  r[i]='缺同日预测快照' if i not in [15,16,17,34,36] else '无历史锁定预测'
 r[22]='2026-10-27';r[23]=float(x['pct'].replace('%','').replace(',',''))
 for i in range(51,55):r[i]='未取得分部披露'
 r+= [x['group'],x['classification'],x['reason'],float(x['price'].replace('$','').replace(',','')),'Nasdaq行情；基准2026-10-27；GICS公开映射或主营业务暂映射。市值/利润单位亿美元；未取得数据不填0。']
 rows.append(r)
pathlib.Path('work/base_values.json').write_text(json.dumps(rows,ensure_ascii=False))
t,ss=connect()
before=api('GET',f'sheets/v2/spreadsheets/{ss}/values/K3baGL!A1:BC203',t)
pathlib.Path('work/target_full_backup.json').write_text(json.dumps(before,ensure_ascii=False))
result=api('POST',f'sheets/v2/spreadsheets/{ss}/sheets_batch_update',t,{'requests':[{'updateSheet':{'properties':{'sheetId':'K3baGL','gridProperties':{'rowCount':max(500,len(rows)),'columnCount':60}}}}]})
print('resize',result)
for start in range(0,len(rows),100):
 batch=rows[start:start+100]
 api('PUT',f'sheets/v2/spreadsheets/{ss}/values',t,{'valueRange':{'range':f'K3baGL!A{start+1}:BH{start+len(batch)}','values':batch}})
 print('wrote',start+1,start+len(batch),flush=True)
print('companies',len(pool),'groups',len(collections.Counter(x['group'] for x in pool)))
