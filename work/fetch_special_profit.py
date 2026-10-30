import json,pathlib,subprocess,concurrent.futures
root=pathlib.Path('work/special_profit');root.mkdir(exist_ok=True)
rows=json.load(open('work/special_live_before.json'))['data']['valueRange']['values'][1:]
jobs=[]
for r in rows:
 if not r[3]:continue
 if not isinstance(r[11],(float,int)) or not isinstance(r[50],(float,int)):jobs.append((r[3],'annual'))
 if any(not isinstance(x,(int,float)) for x in r[12:15]):jobs.append((r[3],'forecast'))
def fetch(job):
 s,k=job;p=root/(s+'_'+k+'.json');sym=s.replace('.','%2F')
 path=f'company/{sym}/financials?frequency=1' if k=='annual' else f'analyst/{sym}/earnings-forecast'
 try:
  result=subprocess.run(['curl','--silent','--show-error','--fail','--max-time','25','-A','Mozilla/5.0','https://api.nasdaq.com/api/'+path],capture_output=True,text=True,check=True)
  d=json.loads(result.stdout)
  p.write_text(json.dumps(d));return s,k,bool(d.get('data'))
 except Exception as e:return s,k,str(e)
with concurrent.futures.ThreadPoolExecutor(5) as ex:
 for x in ex.map(fetch,jobs):print(x,flush=True)
