import sys,json
sys.path.insert(0,'work');from feishu_api import connect,api
t,s=connect();b=f'sheets/v2/spreadsheets/{s}'
rows=api('GET',b+'/values/K3baGL!A1:BT459?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values'];row=next(i+1 for i,r in enumerate(rows) if len(r)>3 and r[3]=='SKHY');print('row',row)
api('PUT',b+'/values',t,{'valueRange':{'range':f'K3baGL!G{row}:G{row}','values':[[7.80]]}})
api('PUT',b+'/values',t,{'valueRange':{'range':f'K3baGL!BI{row}:BJ{row}','values':[['https://companiesmarketcap.com/sk-hynix/pe-ratio/','TTM PE=7.79958，网页标注截至2026年10月；按公开页面直接补入，SK hynix的Nasdaq财报接口无数据。该页面使用韩国上市主体000660.KS口径，ADR价格口径可能存在差异。']]}})
a=api('GET',b+f'/values/K3baGL!G{row}:G{row}?valueRenderOption=UnformattedValue',t)['data']['valueRange']['values'][0][0];assert abs(a-7.8)<1e-9;print('verified',row,a)
