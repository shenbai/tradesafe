# coding: utf-8

#历史数据
history_api = 'http://q.stock.sohu.com/hisHq?code=cn_600153&start=20141010&end=20160620&stat=1&order=D&period=d'

# 历史大单数据
history_bill = 'http://vip.stock.finance.sina.com.cn/quotes_service/view/cn_bill_download.php?symbol=sh600000&num=6000&page=1&sort=ticktime&asc=0&volume=40000&amount=0&type=0&day=2016-06-20'

# 内部交易
nbjy_api = 'http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/nbjy/index.phtml?bdate=2016-05-01&edate=2016-06-20&num=600'
# http://q.stock.sohu.com/app2/rpsholder.up
# http://q.stock.sohu.com/app2/rpsholder.up?code=002551&sd=2015-12-20&ed=2016-6-20&type=date&dir=1
#融资融券
# http://q.stock.sohu.com/app2/mpssTrade.up?code=000001&sd=2016-6-13&ed=2016-6-20
# http://data.10jqka.com.cn/market/rzrq/

#大宗交易
# http://data.10jqka.com.cn/market/dzjy/field/enddate/order/desc/page/1/ajax/1/
#资金流向
# http://data.10jqka.com.cn/funds/gnzjl/###

indices = {
    'zs_000001': '上证指数',
    'zs_000002': 'Ａ股指数',
    'zs_000003': 'Ｂ股指数',
    'zs_000004': '工业指数',
    'zs_000005': '商业指数',
    'zs_000006': '地产指数',
    'zs_000007': '公用指数',
    'zs_000008': '综合指数',
    'zs_000010': '上证180',
    'zs_000011': '沪市基金',
    'zs_000012': '国债指数',
    'zs_000013': '企债指数',
    'zs_000015': '红利指数',
    'zs_000016': '上证50',
    'zs_000017': '新综指',
    'zs_000019': '治理指数',
    'zs_000042': '上证央企',
    'zs_000043': '超大盘',
    'zs_000049': '上证民企',
    'zs_000054': '上证海外',
    'zs_000055': '上证地企',
    'zs_000056': '上证国企',
    'zs_000057': '全指成长',
    'zs_000058': '全指价值',
    'zs_000059': '全R成长',
    'zs_000060': '全R价值',
    'zs_000061': '沪企债30',
    'zs_000062': '上证沪企',
    'zs_000063': '上证周期',
    'zs_000064': '非周期',
    'zs_000066': '上证商品',
    'zs_000067': '上证新兴',
    'zs_000159': '沪股通',
    'zs_000300': '沪深300',
    'zs_000903': '中证100',
    'zs_000905': '中证500',
    'zs_000906': '中证800',
    'zs_000914': '300金融',
    'zs_000922': '中证红利',
    'zs_000964': '中证新兴',
    'zs_000999': '两岸三地',
    'zs_399001': '深证成指',
    'zs_399002': '深成指R',
    'zs_399003': '成份Ｂ指',
    'zs_399004': '深证100R',
    'zs_399005': '中小板指',
    'zs_399006': '创业板指',
    'zs_399007': '深证300',
    'zs_399008': '中小300',
    'zs_399101': '中小板综',
    'zs_399102': '创业板综',
    'zs_399106': '深证综指',
    'zs_399107': '深证Ａ指',
    'zs_399108': '深证Ｂ指',
    'zs_399300': '沪深300',
    'zs_399305': '深市基金',
    'zs_399352': '深报综指',
    'zs_399369': 'CBN-兴全',
    'zs_399481': '企债指数',
    'zs_399606': '创业板R'
}
