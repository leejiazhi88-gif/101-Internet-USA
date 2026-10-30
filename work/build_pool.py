import csv,json,re,collections
sp={x['Symbol']:x for x in csv.DictReader(open('work/sp500.csv'))}
groups={
'1010':('能源','能源'), '1510':('原材料','原材料'), '2010':('工业','资本货物'),'2020':('工业','商业和专业服务'),'2030':('工业','运输'),
'2510':('可选消费','汽车与汽车零部件'),'2520':('可选消费','耐用消费品与服装'),'2530':('可选消费','消费者服务'),'2550':('可选消费','可选消费品经销与零售'),
'3010':('必需消费','必需消费品经销与零售'),'3020':('必需消费','食品饮料与烟草'),'3030':('必需消费','家庭与个人用品'),
'3510':('医疗保健','医疗保健设备与服务'),'3520':('医疗保健','制药生物科技与生命科学'),
'4010':('金融','银行'),'4020':('金融','金融服务'),'4030':('金融','保险'),
'4510':('信息技术','软件与服务'),'4520':('信息技术','技术硬件与设备'),'4530':('信息技术','半导体与半导体设备'),
'5010':('通信服务','电信服务'),'5020':('通信服务','媒体与娱乐'),'5510':('公用事业','公用事业'),
'6010':('房地产','权益型房地产投资信托'),'6020':('房地产','房地产管理与开发')}
subgroups={}
def m(g,s):
 for x in s.split('|'):subgroups[x]=g
m('2020','Diversified Support Services|Environmental & Facilities Services|Human Resource & Employment Services|Research & Consulting Services|Data Processing & Outsourced Services|Office Services & Supplies|Security & Alarm Services|Commercial Printing')
m('2030','Air Freight & Logistics|Cargo Ground Transportation|Passenger Airlines|Passenger Ground Transportation|Rail Transportation|Airport Services|Highways & Railtracks|Marine Transportation|Marine Ports & Services')
m('2510','Automobile Manufacturers|Automotive Parts & Equipment|Motorcycle Manufacturers|Tires & Rubber')
m('2520','Apparel, Accessories & Luxury Goods|Footwear|Homebuilding|Consumer Electronics|Leisure Products|Household Appliances|Home Furnishings|Housewares & Specialties|Textiles')
m('2530','Restaurants|Hotels, Resorts & Cruise Lines|Casinos & Gaming|Specialized Consumer Services|Education Services|Leisure Facilities')
m('2550','Apparel Retail|Automotive Retail|Broadline Retail|Computer & Electronics Retail|Distributors|Home Improvement Retail|Homefurnishing Retail|Other Specialty Retail')
m('3010','Consumer Staples Merchandise Retail|Food Distributors|Food Retail|Drug Retail')
m('3030','Household Products|Personal Care Products')
m('3510','Health Care Distributors|Health Care Equipment|Health Care Facilities|Health Care Services|Health Care Supplies|Health Care Technology|Managed Health Care')
m('4010','Diversified Banks|Regional Banks')
m('4030','Insurance Brokers|Life & Health Insurance|Multi-line Insurance|Property & Casualty Insurance|Reinsurance')
m('4520','Communications Equipment|Electronic Components|Electronic Equipment & Instruments|Electronic Manufacturing Services|Technology Distributors|Technology Hardware, Storage & Peripherals')
m('4530','Semiconductors|Semiconductor Materials & Equipment')
m('5010','Integrated Telecommunication Services|Wireless Telecommunication Services|Alternative Carriers')
m('6020','Real Estate Services|Real Estate Development|Diversified Real Estate Activities|Real Estate Operating Companies')
def getgroup(x):
 s=x['GICS Sector']; sub=x['GICS Sub-Industry']
 if sub in subgroups:return subgroups[sub]
 return {'Energy':'1010','Materials':'1510','Industrials':'2010','Consumer Discretionary':None,'Consumer Staples':'3020','Health Care':'3520','Financials':'4020','Information Technology':'4510','Communication Services':'5020','Utilities':'5510','Real Estate':'6010'}[s]
manual={}
def a(g,t):
 for s in t.split():manual[s]=g
a('1010','BP CCJ CNQ CQP CVE E EC ENB EPD EQNR IMO LNG MPLX PBR SHEL SU TRP TS TTE VG WDS')
a('1510','AEM AU B BHP FNV GFI MT NTR RIO SCCO VALE WPM')
a('2010','ESLT HEI RKLB SPCX SUNB')
a('2020','RELX TRI WCN')
a('2030','CNI CP FER')
a('2510','HMC RACE TM')
a('2520','SONY')
a('2530','QSR VIK')
a('2550','BABA JD MELI PDD SE')
a('3010','FMX')
a('3020','ABEV BTI BUD CCEP DEO')
a('3030','UL')
a('3510','ALC MDLN')
a('3520','ALNY ARGX AZN GSK HLN NTRA NVO NVS ONC RPRX RVMD SNY TAK TEVA')
a('4010','BBD BBVA BCS BMO BNS BSBR CM DB HDB HSBC IBN ING ITUB KB LYG MFG MUFG NU NWG RY SAN SHG SMFG TD')
a('4020','BAM BN IX RKT UBS')
a('4030','MFC SLF')
a('4510','BSP CRWV INFY MDB MSTR NBIS NET OKTA SAP SHOP SNOW TEAM ZS')
a('4520','ERIC NOK UI')
a('4530','ALAB ARM ASML ASX SKHY STM TSM UMC')
a('5010','AMX CHT VOD')
a('5020','NTES RBLX SPOT')
a('5510','NGG')
a('6020','BEKE JLL FSV CWK HHH OPEN VTMX')
r=json.load(open('work/nasdaq_latest.json'))['data']['rows']; out=[]; excluded=[]
for x in r:
 s=x['symbol'].replace('/','.');name=x['name'];cap=float(x.get('marketCap') or 0)
 # Exclude securities rather than operating-company ordinary/ADR listings. ITUB is a valid ADR of preferred equity, retained as issuer representative.
 if re.search(r'warrant|notes due|debenture|tangible equity unit|corporate units|ZONES|mandatory convertible|perpetual.*preferred|series.*preferred',name,re.I) or (re.search('preferred',name,re.I) and s!='ITUB'):
  continue
 if s in ['BRK.A','GOOG','BBDO','GOOGM','GOOGN']:continue
 if s not in sp and s not in manual and cap<3e10:continue
 gx=sp.get(s);g=getgroup(gx) if gx else manual.get(s)
 if not g:
  print('UNMAPPED',s,name);continue
 if cap<=0:continue
 clean=re.split(r' Common Stock| Class [A-Z] | American Depositary| Ordinary Shares| Common Shares| ADS| Sponsored ADR| New York Registry',name)[0].strip()
 out.append({'ticker':s,'name':clean,'cap':cap,'group':g,'sector_cn':groups[g][0],'group_cn':groups[g][1],'subindustry':gx['GICS Sub-Industry'] if gx else '', 'classification':'公开GICS映射' if gx else '按主营业务映射GICS，待官方核验','industry_raw':x['industry'],'pct':x['pctchange'],'price':x['lastsale'],'country':x['country']})
by=collections.defaultdict(list)
for x in out:by[x['group']].append(x)
selected=[]
for g in groups:
 ranked=sorted(by[g],key=lambda x:-x['cap'])
 for i,x in enumerate(ranked):
  if x['cap']>=3e10 or i<2:
   x['reason']='市值≥300亿美元' if x['cap']>=3e10 else '二级行业前二补足（公开候选池）';selected.append(x)
selected.sort(key=lambda x:(x['group'],-x['cap']))
json.dump(selected,open('work/pool.json','w'),ensure_ascii=False)
print('selected',len(selected),'groups',len(set(x['group'] for x in selected)),'counts',dict(collections.Counter(x['group'] for x in selected)))
print('supplements',[(x['ticker'],x['group'],x['cap']) for x in selected if x['cap']<3e10])
