import importlib.util,json,pathlib
p='/Users/fuguiplus/Documents/Codex/2026-10-20/9/scripts/feishu_sheet.py'
spec=importlib.util.spec_from_file_location('existing_feishu',p);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
def connect():
 cfg={}
 for line in pathlib.Path('/Users/fuguiplus/Documents/Codex/2026-05-06/obsdian/.env').read_text().splitlines():
  if '=' in line and not line.lstrip().startswith('#'):
   k,v=line.split('=',1);cfg[k.strip()]=v.strip().strip('"\'')
 token=helper.request('POST','auth/v3/tenant_access_token/internal',body={'app_id':cfg['FEISHU_APP_ID'],'app_secret':cfg['FEISHU_APP_SECRET']})['tenant_access_token']
 wiki_token=cfg.get('FEISHU_WIKI_TOKEN')
 if not wiki_token:
  raise ValueError('Missing FEISHU_WIKI_TOKEN in local credentials')
 node=helper.request('GET','wiki/v2/spaces/get_node?token='+wiki_token,token)['data']['node']
 assert node['obj_type']=='sheet'
 return token,node['obj_token']
def api(method,path,token,body=None):return helper.request(method,path,token,body)
if __name__=='__main__':
 token,ss=connect();meta=api('GET',f'sheets/v3/spreadsheets/{ss}/sheets/query',token);pathlib.Path('work/sheet_meta.json').write_text(json.dumps(meta,ensure_ascii=False));print('Connected. Sheets:',[(x['sheet_id'],x['title']) for x in meta['data']['sheets']]);
 vals=api('GET',f'sheets/v2/spreadsheets/{ss}/values/K3baGL!A1:CB4',token);pathlib.Path('work/target_before.json').write_text(json.dumps(vals,ensure_ascii=False));print('Values:',json.dumps(vals['data']['valueRange'].get('values'),ensure_ascii=False))
