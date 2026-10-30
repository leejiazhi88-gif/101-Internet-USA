import json,pathlib
prepared=json.load(open('work/composition/prepared.json'))
out=[]
cn={'Tubes':'钢管','Other':'其他','Investment Bank':'投资银行','Private Bank':'私人银行','Asset Management (AM)':'资产管理','Corporate & Other (C&O)':'总部及其他','Corporate Bank':'企业银行','Commercial Banking':'商业银行','Global Wholesale Banking':'全球批发银行','Proportionally Consolidated Companies':'按比例合并公司调整','Unallocated Adjustments':'未分配调整','Eliminations':'内部抵销','Insurance, Pension Plans and Capitalization':'保险、养老金及资本化业务','Banking Activities':'银行业务','Consolidation Adjustments':'合并调整','Other Activities':'其他业务'}
for s,date in [('TS','2026-03-31'),('DB','2026-06-30'),('BSBR','2026-03-31'),('BBD','2026-03-31')]:
 d=json.load(open(f'work/composition/parsed/{s}_quarter.json'));idx=d['datekey'].index(date)
 items=[(d['titles'].get(k,k),vs[idx]) for k,vs in d['categories']['Revenue by Segment'].items() if isinstance(vs[idx],(float,int))]
 total=next((v for t,v in items if t=='Total'),None);items=[(t,v) for t,v in items if t!='Total']
 unit={'USD':'亿美元','EUR':'亿欧元','BRL':'亿雷亚尔'}[d['details']['currency']]
 additive=total is not None and abs(sum(v for t,v in items)-total)<max(abs(total)*.001,1)
 text=[f'替代期：单季截至{date}｜分部收入｜{unit}']
 for title,val in sorted(items,key=lambda z:-abs(z[1])):
  pct=f'（{val/total*100:.1f}%）' if additive else ''
  text.append(f'{cn[title]}：{val/1e8:.2f}{pct}')
 if total is not None:text.append(f'合计：{total/1e8:.2f}')
 if not additive:text.append('未提供同口径合计，仅列金额')
 if additive and any(v<0 for t,v in items):text.append('含亏损/总部抵销，正贡献占比可超过100%')
 source=f'https://stockanalysis.com/stocks/{s.lower()}/financials/metrics/?p=quarterly'
 out.append({'ticker':s,'column':'AJ','value':'\n'.join(text),'source':source,'period':date,'note':f'2026年最新一期公开页面无可用分部收入值，回溯到能取得的最近单季{date}；不是全年或累计数据，未跨年替代。来源StockAnalysis/S&P Global，检索2026-10-28。','verified':True,'method':'earlier_quarter_same_year','items':items,'currency':d['details']['currency']})
pathlib.Path('work/special_composition_candidates.json').write_text(json.dumps({'candidates':out,'missing':[]},ensure_ascii=False,indent=2))
print(len(out))
