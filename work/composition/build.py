import json,pathlib,re,collections,datetime,math
ROOT=pathlib.Path('work/composition/parsed');POOL=json.load(open('work/pool.json'));CUTOFF='2026-10-27'
# Keep original proper names when no dependable Chinese label is available.
phrases={'Compute & Networking':'计算与网络','Graphics':'图形','Hyperscale':'超大规模云客户','AI Clouds, Industrial, & Enterprise':'AI云、工业与企业','Edge Computing':'边缘计算','Data Center':'数据中心','Gaming':'游戏','Professional Visualization':'专业可视化','Automotive':'汽车','OEM & Other':'OEM及其他','Productivity & Business Processes':'生产力与业务流程','Intelligent Cloud':'智能云','More Personal Computing':'个人计算','Services':'服务','Wearables, Home and Accessories':'可穿戴、家居及配件','Americas':'美洲','Greater China':'大中华区','Rest of Asia Pacific':'其他亚太地区','North America':'北美','South America':'南美','United States':'美国','U.S.':'美国','Non-U.S.':'非美国','Europe':'欧洲','International':'国际','Rest of World':'其他地区','Other Countries':'其他国家','Canada':'加拿大','Japan':'日本','China':'中国','Latin America':'拉美','Asia Pacific':'亚太','Asia-Pacific':'亚太','EMEA':'欧洲、中东及非洲','APAC':'亚太','Asia':'亚洲','Australia':'澳大利亚','Germany':'德国','United Kingdom':'英国','UK':'英国','Netherlands':'荷兰','Financial Services':'金融服务','Financial Products':'金融产品','Upstream':'上游开采','Downstream':'下游炼化','Energy Products':'能源产品','Chemical Products':'化工产品','Specialty Products':'特种产品','Integrated Gas':'综合天然气','Marketing':'营销','Chemicals and Products':'化工及成品油','Renewables and Energy Solutions':'可再生能源与能源解决方案','Refining & Marketing':'炼油与营销','Midstream':'中游运输','Exploration & Production':'勘探与生产','Natural Gas Liquids':'天然气液体','Natural Gas':'天然气','Crude Oil':'原油','Liquefied Natural Gas':'液化天然气','Copper':'铜','Iron Ore':'铁矿石','Gold':'黄金','Silver':'白银','Zinc':'锌','Coal':'煤炭','Aluminum':'铝','Potash':'钾肥','Nitrogen':'氮肥','Phosphate':'磷肥','Industrial':'工业','Aerospace':'航空航天','Defense':'国防','Construction Industries':'工程机械','Resource Industries':'资源机械','Energy & Transportation':'能源与运输','Commercial Airplanes':'民用飞机','Defense, Space & Security':'国防、航天及安全','Global Services':'全球服务','Commercial Banking':'商业银行','Retail Banking':'零售银行','Wholesale Banking':'批发银行','Consumer Banking':'消费者银行','Investment Banking':'投资银行','Asset Management':'资产管理','Wealth Management':'财富管理','Global Markets':'全球市场','Global Banking':'全球银行','Institutional Securities':'机构证券','Personal Banking':'个人银行','Investment Management':'投资管理','Consumer & Community Banking':'消费者与社区银行','Corporate & Investment Bank':'企业与投资银行','Asset & Wealth Management':'资产与财富管理','Insurance':'保险','Reinsurance':'再保险','Credit':'信贷','Private Equity':'私募股权','Real Estate':'房地产','Infrastructure':'基础设施','Oncology':'肿瘤','Neuroscience':'神经科学','Immunology':'免疫','Vaccines':'疫苗','Medical Devices':'医疗器械','Medical':'医疗','Nutrition':'营养品','Diagnostics':'诊断','Pharmaceutical':'制药','Animal Health':'动物健康','Life Sciences':'生命科学','Instruments':'仪器','Laboratory':'实验室','Software':'软件','Hardware':'硬件','Subscription':'订阅','Advertising':'广告','Online Stores':'线上自营商店','Physical Stores':'实体店','Third-Party Seller Services':'第三方卖家服务','Subscription Services':'订阅服务','Google Search & Other':'谷歌搜索及其他','YouTube Ads':'YouTube广告','Google Network':'谷歌广告联盟','Google Cloud':'谷歌云','Google Services':'谷歌服务','Other Bets':'其他创新业务','Family of Apps':'应用家族','Reality Labs':'现实实验室','Semiconductor Solutions':'半导体解决方案','Infrastructure Software':'基础设施软件','DRAM':'DRAM存储','NAND':'NAND闪存','Mobile':'移动','Communication':'通信','Networks':'网络','Network':'网络','Client':'客户端','Embedded':'嵌入式','Computing':'计算','Storage':'存储','Enterprise':'企业','Cloud':'云','Products':'产品','Product':'产品','Equipment':'设备','Consumer':'消费者','Commercial':'商业','Retail':'零售','Wholesale':'批发','Transportation':'运输','Freight':'货运','Intermodal':'多式联运','Electric':'电力','Gas':'燃气','Regulated':'受监管','Generation':'发电','Transmission':'输电','Distribution':'分销','Digital':'数字','Operating':'经营','Domestic':'国内','Other Segment':'其他分部','Other Product':'其他产品','Corporate & Other':'总部及其他','Corporate and Other':'总部及其他','Corporate':'总部','All Other':'其他','Other':'其他','Eliminations':'内部抵销','Elimination':'内部抵销','Intersegment':'分部间','Service':'服务'}
catlabels={'Revenue':'收入','Revenue Breakdown':'业务收入','Revenue by Segment':'分部收入','Revenue by Geography':'地区收入','Net Revenue':'净收入','Net Revenue by Geography':'地区净收入','Net Income':'净利润','Net Income by Geography':'地区净利润','EBIT':'营业利润（EBIT）','EBIT by Geography':'地区营业利润','EBT':'税前利润','EBT by Geography':'地区税前利润','Adjusted Net Income':'调整后净利润','Adjusted EBIT':'调整后营业利润','Adjusted EBIT by Geography':'地区调整后营业利润','Adjusted EBT':'调整后税前利润','Gross Profit':'毛利润','Gross Profit by Geography':'地区毛利润','Adjusted Gross Profit':'调整后毛利润','EBITDA':'息税折旧摊销前利润','EBITDA by Geography':'地区EBITDA','Adjusted EBITDA':'调整后EBITDA','Adjusted EBITDA by Geography':'地区调整后EBITDA','Funds From Operations':'运营资金FFO（非净利润）','Fee Related Earnings':'费用相关收益（非净利润）','Distributable Earnings':'可分配收益（非净利润）'}
profitpriority=['Net Income','Net Income by Geography','EBIT','EBIT by Geography','EBT','EBT by Geography','Adjusted Net Income','Adjusted EBIT','Adjusted EBIT by Geography','Adjusted EBT','Gross Profit','Gross Profit by Geography','Adjusted Gross Profit','EBITDA','EBITDA by Geography','Adjusted EBITDA','Adjusted EBITDA by Geography','Funds From Operations','Fee Related Earnings','Distributable Earnings']
revpriority=['Revenue','Revenue Breakdown','Revenue by Segment','Net Revenue','Revenue by Geography','Net Revenue by Geography']
currencies={'USD':'亿美元','EUR':'亿欧元','KRW':'亿韩元','JPY':'亿日元','TWD':'亿新台币','CNY':'亿元人民币','CAD':'亿加元','GBP':'亿英镑','CHF':'亿瑞郎','BRL':'亿雷亚尔','INR':'亿卢比'}

def cnlabel(title):
 if title.startswith('Eliminations from '):return '内部抵销'
 exact={'Operating Income (Other)':'总部及其他调整','Revenue (Other)':'其他收入','Gross Profit (Other)':'其他毛利','Eliminations from Revenue':'内部抵销'}
 if title in exact:return exact[title]
 for suffix in [' Income Before Taxes',' Adjusted Operating Income',' Operating Income',' Segment Profit',' Operating Profit',' Adjusted Net Income',' Net Income',' Adjusted EBITDA',' Adjusted EBIT',' EBITDA',' EBIT',' EBT',' Gross Profit',' Revenue',' CCS Earnings',' Earnings']:
  title=title.replace(suffix,'')
 # Long phrases first, protected with markers to avoid translating the same text repeatedly.
 keep={}
 for j,(en,zh) in enumerate(sorted(phrases.items(),key=lambda z:-len(z[0]))):
  token=f'§{j}§'
  if en in title:title=title.replace(en,token);keep[token]=zh
 for token,zh in keep.items():title=title.replace(token,zh)
 return title.strip()

def load(s,k):
 p=ROOT/(s+'_'+k+'.json')
 try:return json.loads(p.read_text())
 except:return {}

def basecat(c):return re.sub(r' \d+$','',c)

def candidates(d,idx,kind):
 choices=[];priority=revpriority if kind=='rev' else profitpriority
 for cat,rawrows in d.get('categories',{}).items():
  bc=basecat(cat)
  if bc not in priority:continue
  vals=[];totals=[]
  for key,vs in rawrows.items():
   if idx>=len(vs) or not isinstance(vs[idx],(int,float)):continue
   v=vs[idx];title=d.get('titles',{}).get(key,key)
   if re.search(r'\b(growth|margin|per share|per unit|percentage|ton miles)\b',title,re.I):continue
   istotal=bool(re.search(r'\(Total\)$',title,re.I)) or key in ['revenue_total','operating_income_total','net_income_total','income_before_taxes_total','adjusted_ebitda_total','gross_profit_total']
   if istotal:totals.append((title,v))
   else:vals.append((title,v))
  # Exclude standalone total measures incorrectly placed under a category.
  if not vals:continue
  total=totals[0][1] if totals else None
  # Apple product subtotal duplicates its four individually disclosed products.
  leaves=[v for t,v in vals if t in ['iPhone Revenue','Mac Revenue','iPad Revenue','Wearables, Home and Accessories Revenue']]
  if len(leaves)==4:
   vals=[(t,v) for t,v in vals if not (t=='Products Revenue' and abs(v-sum(leaves))<1)]
  additive=total is not None and abs(total)>0 and abs(sum(v for k,v in vals)-total)<=max(abs(total)*.015,1)
  score=(0 if additive else 1,priority.index(bc),0 if cat==bc else 1,len(vals))
  choices.append((score,cat,vals,total,additive))
 return sorted(choices,key=lambda c:c[0])

def select(d,year):
 dates=d.get('datekey',[])
 matches=[(date,i) for i,date in enumerate(dates) if date.startswith(str(year)+'-') and date<=CUTOFF]
 return max(matches) if matches else None

def build_cell(s,year,kind,a,q):
 options=[]
 annual=select(a,year)
 if annual:options.append((annual[0],1,a,annual[1],'年度'))
 if year==2026:
  quarter=select(q,year)
  if quarter:options.append((quarter[0],0,q,quarter[1],'单季'))
 # Latest available dated report, annual beats Q4 on same period end.
 options.sort(key=lambda z:(z[0],z[1]),reverse=True)
 for date,_,d,idx,period in options:
  cs=candidates(d,idx,kind)
  if not cs:continue
  if s in ['TSM','SKHY'] and kind=='rev':
   preferred=[c for c in cs if c[1]=='Revenue Breakdown 2' and c[4]]
   if preferred:cs=preferred
  _,cat,vals,total,additive=cs[0];bc=basecat(cat);metric=catlabels.get(bc,bc)
  currency=(d.get('details') or {}).get('currency')
  if not currency:continue
  unit=currencies.get(currency,'亿'+currency)
  # Negative components kept as negative contributions; no fabricated residuals.
  vals=sorted(vals,key=lambda z:-abs(z[1]));render=vals[:7]
  omitted=vals[7:]
  if omitted and additive:render.append((f'其余{len(omitted)}项合计',sum(v for _,v in omitted)))
  lines=[f'{period}截至{date}｜{metric}｜{unit}']
  for title,val in render:
   pct=f'（{val/total*100:.1f}%）' if additive and total is not None and total>0 else ''
   lines.append(f'{cnlabel(title)}：{val/1e8:.2f}{pct}')
  if total is not None:lines.append(f'合计：{total/1e8:.2f}')
  if not additive:lines.append(('未提供同口径合计，仅列金额' if total is None else '分项与合计未核对一致，不计算占比')+('；仅列主要7项' if omitted else ''))
  if kind=='profit' and bc!='Net Income':lines.append('以上不是归母净利润分拆')
  if additive and any(v<0 for _,v in vals):lines.append('含亏损/总部抵销，正贡献占比可超过100%')
  url=f'https://stockanalysis.com/stocks/{s.lower().replace(".","-")}/financials/metrics/'+('?p=quarterly' if period=='单季' else '')
  return '\n'.join(lines),{'period':period,'date':date,'metric':metric,'category':cat,'unit':currency,'additive':additive,'source':url,'items':vals,'total':total}
 msg=f'{year}年：所取公开页面未取得'+('该期分部收入数值' if kind=='rev' else '该期分部利润数值，不能据收入占比分摊')
 return msg,{'missing':True}

phrases.update({'Wafer':'晶圆','Other Product & Service':'其他产品及服务','Commercial & Investment Bank':'商业及投资银行','Corporate and Financing':'总部及融资','Energy':'能源','High Performance Computing':'高性能计算','Smartphone':'智能手机','Internet of Things':'物联网','Digital Consumer Electronics':'数字消费电子','Other Platform':'其他平台','NAND Flash':'NAND闪存'})
results={};stats=collections.Counter()
for x in POOL:
 s=x['ticker'];a=load(s,'annual');q=load(s,'quarter');vals=[];audits=[]
 for col,year,kind in [('AH',2025,'rev'),('AI',2025,'profit'),('AJ',2026,'rev'),('AK',2026,'profit')]:
  text,audit=build_cell(s,year,kind,a,q);vals.append(text);audits.append(audit);stats[col+('_missing' if audit.get('missing') else '_filled')]+=1
 results[s]={'values':vals,'audit':audits,'sources':'\n'.join(dict.fromkeys(z['source'] for z in audits if z.get('source')))}
pathlib.Path('work/composition/prepared.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
pathlib.Path('work/composition/summary.json').write_text(json.dumps(dict(stats)))
print(dict(stats))
for s in ['NVDA','AAPL','MSFT','XOM','JPM','TSM','SKHY']:
 print(s,results[s]['values'])
