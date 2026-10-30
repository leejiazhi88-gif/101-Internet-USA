import json,pathlib,datetime,collections
pool=json.load(open('work/pool.json'));rows=json.load(open('work/base_values.json'));base=datetime.datetime(2026,10,27)
def num(v):
 try:return float(str(v).replace('$','').replace(',','').replace('%',''))
 except:return None
stats=collections.Counter()
for c,n in [(24,10),(25,30),(26,60),(27,90),(28,250),(29,360),(31,720),(32,1080)]:rows[0][c]=str(n)+'自然日价格涨幅%（源收盘价）'
rows[0][30]='360自然日收盘峰值至今涨幅%'
for r,x in zip(rows[1:],pool):
 s=x['ticker'];p=pathlib.Path('work/quote_info/'+s+'.json')
 if p.exists():
  d=json.loads(p.read_text())['data'];date=d.get('primaryData',{}).get('lastTradeTimestamp','')
  if date=='Oct 27, 2026':stats['quote_date_verified']+=1
  else:r[22]='日期待核实'
 hp=pathlib.Path('work/enriched/'+s+'_history.json')
 if hp.exists():
  d=json.loads(hp.read_text()).get('data') or {};a=[]
  for z in (d.get('tradesTable') or {}).get('rows') or []:
   try:dt=datetime.datetime.strptime(z['date'],'%m/%d/%Y');v=num(z['close'])
   except:continue
   if dt<=base and v and v>0:a.append((dt,v))
  a.sort(reverse=True)
  if a and a[0][0]==base:
   stats['history_available']+=1
   for c,n in [(24,10),(25,30),(26,60),(27,90),(28,250),(29,360),(31,720),(32,1080)]:
    v=next((v for dt,v in a if dt<=base-datetime.timedelta(days=n)),None)
    r[c]=round((a[0][1]/v-1)*100,4) if v else '上市历史不足/缺数据'
   r[30]=round((a[0][1]/max(v for dt,v in a if dt>=base-datetime.timedelta(days=360))-1)*100,4)
  else:
   for c in range(24,33):r[c]='缺基准日历史价格'
 else:
  for c in range(24,33):r[c]='历史接口暂未取得'
 r[59]+='价格涨幅按自然日回溯至当日或之前最近交易日，使用Nasdaq Close/Last原值；拆股调整口径未核验，不是含分红总回报。财务披露时点、单位及预测同日快照仍待核验。'
pathlib.Path('work/prepared_values.json').write_text(json.dumps(rows,ensure_ascii=False))
pathlib.Path('work/data_quality.json').write_text(json.dumps(dict(stats),ensure_ascii=False))
print(dict(stats))
