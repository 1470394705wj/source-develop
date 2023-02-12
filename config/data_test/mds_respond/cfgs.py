# -*- coding:utf-8 -*-
# from pprint import pprint
import pprint
import yaml



line_return_sh_sz={'时间':'time',
'开盘价':'open_price',
'最高价':'high_price',
'最低价':'low_price',
'收盘价':'close',
'最新价':'price',
'均价':'avg_price',
'成交量':'volume',
'成交金额':'amount',
'昨收':'prev_close',
'涨跌':'change',
'涨跌幅':'chg_rate',
'振幅':'amp_rate',
'交易阶段':'trd_phase',
'期权持仓量':'open_interest'
}

# line_v1  begin,end,period 需补充用例
line_v1_params_tuples: [
                    # 返回1分钟走势
                    (0, -1, 1),
                    # 返回5分钟走势
                    (0, -1, 5)
                ]


# line v2 begin,end,period,days(-9到0) 需补充用例
line_v2_params_tuples: [
                    # 返回当日1分钟走势
                    (0, -1, 1, ""),
                    # 返回当日5分钟走势
                    (0, -1, 5, ""),
                    # 返回当日1分钟走势
                    (0, -1, 1, 0),
                    # 返回昨日1分钟走势
                    (0, -1, 1, -1),
                    # 返回前9日及今日1分钟走势
                    (0, -1, 1, -9),
                    # 返回当日5分钟走势
                    (0, -1, 5, 0),
                    # 返回昨日5分钟走势
                    (0, -1, 5, -1),
                    # 返回前9日及今日5分钟走势
                    (0, -1, 5, -9)
                ]




order_params=[(0, -1, ""),
(0, -1, "volume,DESC"),
(0, -1, "volume,ASC")]


exchange_self_v1={'CDR证券全称': 'fullname',
 'CDR证券转换基数': 'cdr_base',
 'GDR上市日期': 'gdr_listdate',
 'GDR前一交易日期': 'gdr_prevdate',
 'GDR前收盘价': 'gdr_prevpx',
 'GDR币种': 'gdr_currency',
 'GDR新增股份上市日期': 'gdr_newdate',
 'GDR新增股份产生的原因': 'gdr_newreason',
 'GDR本次上市对应的GDR份额数': 'gdr_base',
 'GDR本次上市的基础股票数': 'gdr_ulbase',
 'GDR转换比例': 'gdr_ratio',
 'iopv': 'iopv',
 'nav sh2需求文档中无此字段': 'nav',
 '上市日期': 'listdate',
 '中文证券名称（长）': 'cpxxextendname',
 '买一': 'bidpx1',
 '交易状态': 'tradingPhaseCode',
 '产品状态标志（同cpxx文件产品状态信息字段）': 'cpxxprodusta',
 '内盘': 'sell_vol',
 '初始流动性生成终止日': 'liquidity_end',
 '初始流动性生成起始日': 'liquidity_start',
 '前日市场流通总量(份)': 'prev_circulation_volume',
 '卖一': 'askpx1',
 '发行价': 'pubprice',
 '地区（省一级）中文名': 'region',
 '均价': 'avg_px',
 '基础证券ISIN代码': 'underlying_isin',
 '基础证券代码': 'underlying_code',
 '基础证券简称': 'underlying_name',
 '基础证券转换基数': 'underlying_base',
 '外盘': 'buy_vol',
 '存托机构代码': 'depository_code',
 '存托机构简称': 'depository_name',
 '对应GDR的证券代码': 'gdr_code',
 '对应GDR的证券简称': 'gdr_name',
 '开盘价': 'open',
 '当前成交量': 'now_vol',
 '总市值': 'totalValue',
 '成交笔数': 'numTrades',
 '成交量': 'volume',
 '成交金额': 'amount',
 '拼音': 'pinyin',
 '振幅': 'amp_rate',
 '换手率': 'turnover_ratio',
 '昨收': 'prev_close',
 '昨结算(深交所期权)': 'presettlepx',
 '是否具有协议控制架构（创业板）同securities文件': 'is_vie',
 '是否有表决权（科创版、创业板）同cpxx、securities文件': 'voting_rights',
 '是否注册制（创业板）同securities文件': 'is_registration',
 '是否盈利（科创版、创业板）同cpxx、securities文件': 'no_profit',
 '最低价': 'low',
 '最新价': 'last',
 '最高价': 'high',
 '沪伦通CDR盘前持仓变更累计数量（份）': 'circulation_change',
 '沪伦通子类别标识': 'hlt_tag',
 '流通市值': 'circulating',
 '涨停价': 'up_limit',
 '涨跌1': 'change',
 '涨跌幅': 'chg_rate',
 '涨跌幅限制类型': 'cpxxlmttype',
 '申万行业分类（一级）中文名': 'swindustry1',
 '申万行业分类（二级）中文名': 'swindustry2',
 '盘后固定价格交易买入申报数量': 'fp_buyvolume',
 '盘后固定价格交易产品实时阶段及标志': 'fp_phase',
 '盘后固定价格交易卖出申报数量': 'fp_sellvolume',
 '盘后固定价格交易成交笔数（深圳创业板）': 'fp_numtrades',
 '盘后固定价格交易成交量': 'fp_volume',
 '盘后固定价格交易成交金额': 'fp_amount',
 '盘后固定价格交易最新成交时间': 'fp_timestamp',
 '结算价(深交所期权)': 'settlepx',
 '证券代码': 'code',
 '证券子类型(同cpxx文件证券子类别字段) ': 'cpxxsubtype',
 '证券简称': 'name',
 '证券类型(同cpxx文件证券类别字段) ': 'cpxxtype',
 '证监会行业分类（一级）中文名': 'industry1',
 '证监会行业分类（二级）中文名': 'industry2',
 '跌停价': 'down_limit',
 '量比': 'volume_ratio'}
#
exchange_self_v2={'CDR证券全称': 'underlying_code',
 'CDR证券转换基数': 'underlying_name',
 'ETF申购数量': 'ETFSellAmount',
 'ETF申购笔数': 'ETFSellNumber',
 'ETF申购金额': 'ETFSellMoney',
 'ETF赎回数量': 'totalWarrantExecQty',
 'ETF赎回笔数': 'yield2Maturity',
 'ETF赎回金额': 'warLowerPx',
 'GDR上市日期': 'gdr_base',
 'GDR前一交易日期': 'cdr_base',
 'GDR前收盘价': 'fullname',
 'GDR币种': 'underlying_base',
 'GDR新增股份上市日期': 'gdr_ulbase',
 'GDR新增股份产生的原因': 'gdr_ratio',
 'GDR本次上市对应的GDR份额数': 'gdr_prevpx',
 'GDR本次上市的基础股票数': 'gdr_prevdate',
 'GDR转换比例': 'gdr_currency',
 'ROE(净资产收益率)': 'weightedAvgBidPx',
 'iopv': 'dynVolume',
 'isin': 'isin',
 'nav sh2需求文档中无此字段': 'pe1',
 '上市日期': 'totalCapital',
 '中文证券名称（长）': 'bid',
 '买一': 'sellQtyUnit',
 '买入委托成交最大等待时间': 'industry1',
 '买入总笔数': 'offerTradeMaxDuration',
 '买入撤单数量': 'withdrawSellAmount',
 '买入撤单笔数': 'withdrawSellNumber',
 '买入撤单金额': 'withdrawSellMoney',
 '买数量单位': 'tradephase',
 '交易分钟数': 'is_vie',
 '交易日': 'tradingDay',
 '交易状态': 'listdate',
 '产品状态标志（同cpxx文件产品状态信息字段）': 'cpxxextendname',
 '产品英文名': 'en',
 '今收盘价': 'close',
 '价格档位': 'securityLendingTag',
 '债券到期收益率': 'warUpperPx',
 '债券加权平均委买价': 'ETFBuyNumber',
 '债券加权平均委卖价': 'ETFBuyMoney',
 '内盘': 'sell_vol',
 '初始流动性生成终止日': 'fp_timestamp',
 '初始流动性生成起始日': 'circulation_change',
 '利率': 'altWeightedAvgBidPx',
 '前日市场流通总量(份)': 'fp_volume',
 '加权平均价涨跌BP': 'withdrawBuyAmount',
 '加权平均委买价': 'altWeightedAvgOfferPx',
 '加权平均委卖价': 'ETFBuyAmount',
 '动态参考价格': 'pe2',
 '动态参考量': 'turnover_ratio',
 '卖一': 'priceUnit',
 '卖出委托成交最大等待时间': 'industry2',
 '卖出总笔数': 'region',
 '卖出撤单数量': 'totalOfferNumber',
 '卖出撤单笔数': 'totalBidNumber',
 '卖出撤单金额': 'bidTradeMaxDuration',
 '卖数量单位': 'financialTag',
 '发行价': 'totalValue',
 '同cpxx-备注字段': 'closeindex3',
 '地区代码': 'regionCode',
 '地区（省一级）中文名': 'swindustry1',
 '均价': 'avg_px',
 '基础证券ISIN代码': 'liquidity_start',
 '基础证券代码': 'depository_code',
 '基础证券简称': 'depository_name',
 '基础证券转换基数': 'underlying_isin',
 '外盘': 'buy_vol',
 '委买': 'totalBid',
 '委卖': 'totalAsk',
 '委差': 'securityType',
 '委托买': 'ask',
 '委托卖': 'askpx1',
 '委比': 'entrustRatio',
 '存托机构代码': 'liquidity_end',
 '存托机构简称': 'prev_circulation_volume',
 '对应GDR的证券代码': 'gdr_newdate',
 '对应GDR的证券简称': 'gdr_newreason',
 '币种': 'cpxxreserved',
 '市价买数量上限': 'mktSQtyUnit',
 '市价卖数量上限': 'refPxType',
 '市净率': 'volume_ratio',
 '市场代码': 'mktcode',
 '市盈率1': 'pbr',
 '市盈率2': 'roe',
 '开盘价': 'open',
 '当前成交量': 'now_vol',
 '当该股票当日无报单时，委比显示为-101.000': 'entrustDiff',
 '总市值': 'estimatedEPS',
 '总股本': 'circulating',
 '成交笔数': 'num_trades',
 '成交量': 'volume',
 '成交金额': 'amount',
 '拼音': 'pinyin',
 '振幅': 'amp_rate',
 '换手率': 'interestRate',
 '收盘指数2': 'voting_rights',
 '收盘指数3': 'trade_min',
 '昨收价': 'prev_close',
 '昨收盘加权平均价': 'withdrawBuyMoney',
 '昨结算(深交所期权)': 'open_interest',
 '是否为融券标的': 'pubprice',
 '是否为融资标的': 'delistDate',
 '是否具有协议控制架构（创业板）同securities文件': 'mktBQtyUnit',
 '是否有表决权（科创版、创业板）同cpxx、securities文件': 'is_registration',
 '是否注册制（创业板）同securities文件': 'mktSQtyUpLimit',
 '是否盈利（科创版、创业板）同cpxx、securities文件': 'eps',
 '最低价': 'low',
 '最新价': 'last',
 '最高价': 'high',
 '期权持仓量(深交所)': 'no_profit',
 '权证执行总数量': 'premiumRate',
 '权证涨停价格': 'avgPrevClose',
 '权证溢价率': 'withdrawBuyNumber',
 '权证跌停价格': 'avgbp',
 '格式为[买一价,买一量,…]': 'bidpx1',
 '格式为[卖一价,卖一量,…]': 'buyQtyUnit',
 '概念代码': 'conceptCode',
 '每股净利润(上年度)': 'iopv',
 '每股净利润(全年预估)': 'nav',
 '每股净资产': 'dynPrice',
 '每股收益': 'mktBQtyUpLimit',
 '沪伦通CDR盘前持仓变更累计数量（份）': 'fp_amount',
 '沪伦通子类别标识': 'gdr_listdate',
 '流通市值': 'bvps',
 '流通股本': 'formerBasicEPS',
 '涨停价': 'up_limit',
 '涨跌 最新价-昨收': 'change',
 '涨跌1 较上一副快照涨跌': 'change1',
 '涨跌幅': 'chg_rate',
 '涨跌幅限制类型': 'cpxxlmttype',
 '申万行业代码': 'swindustryCode',
 '申万行业分类（一级）中文名': 'gdr_code',
 '申万行业分类（二级）中文名': 'gdr_name',
 '盘后固定价格交易买入申报数量': 'fp_numtrades',
 '盘后固定价格交易产品实时阶段及标志': 'presettlepx',
 '盘后固定价格交易卖出申报数量': 'currency',
 '盘后固定价格交易成交笔数（深圳创业板）': 'settlepx',
 '盘后固定价格交易成交量': 'fp_sellvolume',
 '盘后固定价格交易成交金额': 'fp_phase',
 '盘后固定价格交易最新成交时间': 'fp_buyvolume',
 '结算价': 'closeindex2',
 '行业代码': 'industyCode',
 '证券代码': 'code',
 '证券子类型': 'cpxxprodusta',
 '证券简称': 'name',
 '证券简称(中文名)': 'sesname',
 '证券类型': 'securitySubType',
 '证监会行业分类（一级）中文名': 'swindustry2',
 '证监会行业分类（二级）中文名': 'hlt_tag',
 '跌停价': 'down_limit',
 '退市日期': 'tradableShare',
 '量比': 'weightedAvgOfferPx'}
block_v1_v2={'前收盘板块指数': 'preCloseBlockIndex',
 '动态市盈率': 'ttm',
 '委买': 'buyNum',
 '委卖': 'sellNum',
 '委差': 'deviation',
 '委比': 'committee',
 '市净率': 'marketRate',
 '开盘板块指数': 'openBlockIndex',
 '总市值': 'totalMarketValue',
 '总成交量': 'totalTrdVolume',
 '总成交额': 'totalTrdMoney',
 '指数涨跌幅': 'indexChg',
 '振幅': 'amplitude',
 '收盘板块指数': 'closeBlockIndex',
 '最低板块指数': 'lowBlockIndex',
 '最高板块指数': 'highBlockIndex',
 '板块代码': 'code',
 '板块名字': 'name',
 '板块指数': 'blockIndex',
 '板块新代码': 'blockCode',
 '板块流通总值': 'blockFAMC',
 '流通股本': 'tradableShare',
 '涨跌幅': 'upsDowns',
 '涨跌平0涨1跌 2平家数': 'ratioUpDown',
 '静态市盈率': 'lyr'}



#
SERVERS_Cfg = [
  {
    "apitype": "imds",
    "city": "上海",
    "env": "生产",
    "host": "http://180.163.112.215:9266",
    "use": 0
  },
  {
    "apitype": "mds",
    "city": "广州(电信)",
    "env": "生产",
    "host": "http://58.63.252.59:32041",
    "use": 0
  },
  {
    "apitype": "mds",
    "city": "金桥(电信)",
    "env": "生产",
    "host": "http://103.251.85.182:32041",
    "use": 0
  },
  {
    "apitype": "mds",
    "city": "新金桥(电信)",
    "env": "生产",
    "host": "http://180.163.112.215:32041",
    "use": 0
  },
  {
    "apitype": "mds",
    "city": "土城(联通)",
    "env": "生产",
    "host": "http://123.125.111.186:32041",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "全真-新三板-6市场",
    "host": "http://114.80.155.50:32041",
    "use": 0
  },
  {
    "apitype": "mds",
     'city':None,
    "env": "生产",
    "host": "http://yunhq.sse.com.cn:32041",
    "use": 1
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "全真",
    "host": "http://previewyunhq.sse.com.cn:32041",
    "use": 1
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "生产-腾讯云站点-增值",
    "host": "http://119.45.3.10:9267",
    "use": 0
  },
  {
    "apitype": "mds",
     'city':None,
    "env": "生产-增值-内网-老版本",
    "host": "http://103.251.85.66:9267",
    "use": 0
  },
  {
    "apitype": "mds",
'city':None,
    "env": "生产-增值-内网-patch新版本",
    "host": "http://103.251.85.69:9267",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "验收-131",
    "host": "http://10.10.22.131:32041",
    "use": 0
  },
  {
    "apitype": "mds",
   'city':None,
    "env": "验收-132",
    "host": "http://10.10.22.132:32041",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "新三板-腾讯云-生产",
    "host": "http://119.45.3.10:32051",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "新三板-上海-生产",
    "host": "http://114.80.63.3:32051",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "新三板-成都-生产",
    "host": "http://218.6.170.93:32051",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "新三板-广州-生产",
    "host": "http://58.63.252.91:32051",
    "use": 0
  },
  {
    "apitype": "mds",
    'city':None,
    "env": "增值-负载均衡-生产",
    "host": "http://103.251.86.63:9267",
    "use": 0
  }
]
Version_Cfg=['v1','v2']
MarketName_Cfg=[{'MarkeType': 'sh1', 'MarketName': '上交所Level-1行情'},
 {'MarkeType': 'sh2', 'MarketName': '上交所Level-2行情'},
 {'MarkeType': 'sz1', 'MarketName': '深交所Level-1行情'},
 {'MarkeType': 'sz2', 'MarketName': '深交所Level-2行情'}]

TypeNames_Cfg={'type_name': ['exchange', 'self', 'block']}

TypeName=[{'TypeName': 'exchange'}, {'MarketName': 'block'}, {'MarketName': 'self'}]

SubTypeBlock_Cfg={'各申万一级板块代码':'A10001' ,
 '各行业一级板块代码':'占位符' ,
 '显示地区板块的子板块信息': 'region',
 '显示所有板块信息': 'all',
 '显示指数板块的子板块信息': 'index',
 '显示概念板块的子板块信息': 'concept',
 '显示申万板块的子板块信息': 'swhy',
 '显示行业板块的子板块信息': 'industry'}

SubTypeExchange_Cfg={'ST': 'ST',
 '主板A股，以人民币交易': 'ashare',
 '主板B股，以美元交易': 'bshare',
 '地区':'D10001',
 '所有主板': 'main',
 '所有股票': 'stock',
 '所有证券': 'all',
 '指数': '占位符',
 '新债': 'newdebt',
 '新股': 'newstock',
 '概念': '占位符',
 '次新债': 'subnewdebt',
 '次新股': 'subnewstock',
 '申万': '占位符',
 '行业': '占位符',
 '退市整理': 'delistarr',
 '龙虎榜': 'tiger'}

SelfSubtype_code_Cfg={'code1':'513330',
                 'code2':'560010',
                 'code3':'513180',
                 'code4':'513050'
                # 'code5':'513060',
                 # 'code6':'512010',
                  #'code7':'512690',
                #  'code8':'512880'}
                      }
SelfSubtype_SelfCode_Cfg={'selfcode1':'513330_513331'}
ListSelfCode={**SelfSubtype_SelfCode_Cfg,**SelfSubtype_code_Cfg}
Sh1AndSh2Exchange_Cfg={'A股市场证券': 'amarket',
 'B股市场证券': 'bmarket',
 'ETF基金': 'etf',
 'GDR基础股票': 'GDR_underlying',
 'LOF基金': 'lof',
 '上证分级基金': 'structured_fund',
 '买断式债券回购': 'orp',
 '交易所交易基金（买卖）': 'ebs',
 '以人民币交易的股票': 'ash',
 '以人民币交易的股票（科创板）': 'kshare',
 '以美元交易的股票': 'bsh',
 '企业债券': 'cbf',
 '债券(D)': 'bond',
 '公司债券（或地方债券）': 'cpf',
 '公司债（地方债）分销': 'dvp',
 '公开发行优先股': 'ops',
 '其它债券': 'obd',
 '其它基金': 'ofn',
 '其它股票': 'oeq',
 '分离式可转债': 'cbd',
 '可转换企业债券': 'ccf',
 '国债分销': 'dst',
 '国债预发行': 'wit',
 '国际版股票': 'csh',
 '基金(EU)': 'fund',
 '封闭式基金': 'cef',
 '开放式基金': 'oef',
 '报价回购': 'qrp',
 '指数': 'index',
 '无息国债': 'gbz',
 '沪伦通CDR': 'hlt_CDR',
 '沪伦通CDR标的证券': 'hltgdrul',
 '沪市国债': 'gbf',
 '科创板': 'scitech',
 '科创板A股': 'kashare',
 '科创板存托凭证': 'kcdr',
 '股票(ES)': 'equity',
 '质押式企债回购': 'brp',
 '质押式国债回购': 'crp',
 '跨市场/跨境资金': 'fbl',
 '金融机构发行债券': 'fbf',
 '集合资产管理计划': 'amp',
 '非公开发行优先股': 'pps',
 '存托凭证': 'cdr'}
Sz1AndSz2Exchange_Cfg={'ETF期权': 'etf_option',
 'ETF期权（与imds一致）': 'option_etf',
 '个股期权': 'equity_option',
 '中小板股票': 'sme',
 '仅申赎基金': 'purchase_redemption_fund',
 '企业债': 'enterprice_bond',
 '优先股': 'preferred_stock',
 '公司债': 'corporation_bond',
 '分级子基金': 'structured_fund',
 '创业板股票': 'chinext',
 '可交换公司债': 'exchangable_Corporation_bond',
 '可交换私募债': 'exchangeable_Private_raised_bond',
 '可转债': 'convertible',
 '商品期货ETF': 'commodity_future_etf',
 '封闭式基金': 'closed-ended_fund',
 '本市场实物债券ETF': 'physical_bond_etf',
 '本市场股票ETF': 'local_market_etf',
 '权证': 'warrant',
 '杠杆ETF': 'gearing_etf',
 '标准LOF': 'standard_lof',
 '深市国债（含地方债）': 'treasury_bond',
 '深证ETF': 'etf',
 '深证LOF': 'lof',
 '现金债券ETF': 'cash_bond_etf',
 '私募债': 'private_raised_bond',
 '证券公司次级债': 'corporation_subbond',
 '证券公司短期债': 'security_company_short-term_bond',
 '货币ETF': 'currency_etf',
 '质押式回购': 'pledge-style_repo',
 '资产支持证券': 'abs',
 '跨境ETF': 'cross_border_etf',
 '跨市场股票ETF': 'cross_market_etf',
 '黄金ETF': 'gold_etf'}



