import json,datetime,pathlib
base=datetime.date(2026,10,27)
rows=json.load(open('work/composition/publish_after.json'))
result={'baseline_date':base.isoformat(),'retrieved_at':'2026-10-28','candidates':[],'unfilled':[],'warnings':[]}
periods={'Y':10,'Z':30,'AA':60,'AB':90,'AC':250,'AD':360,'AF':720,'AG':1080}
for ticker in ['PLTR','COIN','BRK.B']:
 r=next(x for x in rows if len(x)>3 and x[3]==ticker)
 raw=json.load(open('work/special_history/'+ticker+'.json'))['data']
 assert raw['symbol'].replace('/','.')==ticker
 source=f'https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks&fromdate=2022-06-01&todate=2026-10-27&limit=1500'
 hist=sorted([(datetime.datetime.strptime(x['date'],'%m/%d/%Y').date(),float(x['close'].replace('$','').replace(',',''))) for x in raw['tradesTable']['rows']],reverse=True)
 assert hist[0][0]==base
 close=hist[0][1]
 if close!=r[40]:result['warnings'].append({'ticker':ticker,'column':'AO','sheet_value':r[40],'correct_2026_10_27_close':close,'note':'原AO价格与本次历史API的10/27收盘价不同；本候选仅填缺失Y:AG，不改原AO/X。'})
 for col,days in periods.items():
  target=base-datetime.timedelta(days=days)
  found=next((x for x in hist if x[0]<=target),None)
  if not found or (target-found[0]).days>10:
   result['unfilled'].append({'ticker':ticker,'column':col,'reason':'历史起点最近交易日未在目标日期前10天内取得'});continue
  date,price=found
  note=f'补采Nasdaq历史接口成功，未采用其他基准日；基准2026-10-27收盘{close:.2f}美元；{days}自然日起点{target.isoformat()}按原表规则取当日或此前最近交易日{date.isoformat()}收盘{price:.2f}美元。使用源Close/Last，非含分红总回报，拆股调整口径未独立核验。取数2026-10-28。'
  if close!=r[40]:note+=f'原AO格为{r[40]}美元，与10/27历史收盘不一致；本涨幅统一使用上述历史接口收盘价。'
  result['candidates'].append({'ticker':ticker,'column':col,'value':round(close/price-1,6),'start_date':date.isoformat(),'requested_start_date':target.isoformat(),'end_date':base.isoformat(),'start_price':price,'end_price':close,'source':source,'note':note,'special_case':'原接口缺失，本次同基准日补采成功','mark_red':True})
 window=[x for x in hist if base-datetime.timedelta(days=360)<=x[0]<=base]
 peak_date,peak=max(window,key=lambda x:x[1])
 note=f'补采Nasdaq历史接口成功；窗口{(base-datetime.timedelta(days=360)).isoformat()}至2026-10-27内最高源收盘为{peak_date.isoformat()}的{peak:.2f}美元；末期10/27收盘{close:.2f}美元。以末期/最高收盘-1计算，不使用盘中高价；非含分红总回报，拆股调整口径未独立核验。取数2026-10-28。'
 result['candidates'].append({'ticker':ticker,'column':'AE','value':round(close/peak-1,6),'start_date':peak_date.isoformat(),'requested_start_date':(base-datetime.timedelta(days=360)).isoformat(),'end_date':base.isoformat(),'start_price':peak,'end_price':close,'source':source,'note':note,'special_case':'原接口缺失，本次同基准日补采成功','mark_red':True})
for r in rows[1:]:
 if not r or not r[0]:continue
 for i in range(24,33):
  if r[i]=='上市历史不足/缺数据':
   col=chr(65+i) if i<26 else chr(65+i//26-1)+chr(65+i%26)
   result['unfilled'].append({'ticker':r[3],'column':col,'reason':'原表为上市历史不足/缺数据；未使用不同证券或不足完整观察期的数据代填。'})
result['counts']={'filled':len(result['candidates']),'tickers':3,'unfilled':len(result['unfilled'])}
pathlib.Path('work/special_history_candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result['counts']))
for x in result['candidates']:print(x['ticker'],x['column'],x['value'],x['start_date'],x['end_date'])
print('warnings',result['warnings'])
