import json,pathlib,subprocess,concurrent.futures
root=pathlib.Path('work/special_profit');root.mkdir(exist_ok=True)
rows=json.load(open('work/special_live_before.json'))['data']['valueRange']['values'][1:]
tickers=[r[3] for r in rows if r[3] and not isinstance(r[11],(int,float))]
def fetch(s):
 url=f'https://stockanalysis.com/stocks/{s.lower().replace(".","-")}/financials/'
 try:
  r=subprocess.run(['curl','--silent','--show-error','--fail','--max-time','25','-A','Research contact research@example.com','-H','Accept-Encoding: identity',url],capture_output=True,text=True,check=True)
  (root/(s+'_income.html')).write_text(r.stdout);return s,len(r.stdout)
 except Exception as e:return s,str(e)
with concurrent.futures.ThreadPoolExecutor(5) as ex:
 for x in ex.map(fetch,tickers):print(x,flush=True)
