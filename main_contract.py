import pandas as pd

_FILE_PATH = 'C:/Users/wlk/Desktop/GF Project/Project/Data/'
_SECS = ['RB', 'RM', 'AU', 'AG', 'RU', 'TA', 'M']
_MON = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
_YEAR = ['12', '13', '14', '15', '16', '17']


#   产生万得期货合约代码 注意郑商所升位问题
def generate_code():
    contract_time = [x + y for x in _YEAR for y in _MON]
    contracts = [x + y for x in _SECS for y in contract_time]

    for i, x in enumerate(contracts):
        if x[:2] in ['RB', 'AU', 'AG', 'RU']:
            contracts[i] = x + '.SHF'
        elif x[:2] in ['RM', 'TA']:
            contracts[i] = x + '.CZC'
        elif x[:1] == 'M':
            contracts[i] = x + '.DCE'
    return contracts


#   获取期货合约持仓量并存储
def get_data_oi(code):
    '''
    Parameters
    ----------
    code:RM.SHF RM1609.SHF
    '''
    from WindPy import w
    w.start()
    df = w.wsd(code, "volume,oi", "2010-11-01")
    df.Times = pd.DatetimeIndex([x.date() for x in df.Times])
    df = pd.DataFrame(df.Data, index=df.Fields, columns=df.Times).T
    df.columns = [x.lower() for x in df.columns]
    df = df[df.any(1)]
    if len(df) != 0:
        #   存储所有历史期货合约的持仓信息
        df.to_csv('D:/Data/Futures/History Hold/' + code[:2] + '/' + code + '.csv')


# symbols = generate_code()
# for sec in symbols:
#     get_data_oi(sec)

#   根据持仓量文件信息判断出每日的最大持仓量合约并存储成csv文件
def main_contract_csv(code):
    '''
    code: RU,RM ..
    '''
    import os
    file_path = 'D:/Data/Futures/History Hold/' + code + '/'
    dd = {}
    for x in os.listdir(file_path):
        df = pd.read_csv(file_path + x, index_col=0, parse_dates=True)
        dd[x[:6]] = df[:df.dropna().index[-1]]
    pdata = pd.Panel(dd)
    pdata = pdata.swapaxes('items', 'minor')
    df = pdata['oi']
    res = df.T.apply(lambda df: df.idxmax())
    res.to_csv(_FILE_PATH + code + '_main.csv')


#   查看每个交易日期的主力合约
def main_contract(code):
    '''
    code: AU,AG,M,RU,RB,TA,RM
    '''
    res = {}
    x = pd.read_csv(_FILE_PATH + code + '_main.csv', index_col=0, parse_dates=True, header=None)
    x.columns = ['name']
    x.index.name = 'Date'
    lst = x['name']
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] and (lst[i] in lst[:i].values):
            lst[i] = lst[i - 1]
    return lst


#   查看合约换月日期
def swap_date(code):
    ls = main_contract(code)
    res = {}
    for i, x in enumerate(ls):
        if x != ls[i - 1]:
            res[ls.index[i + 1]] = x
    return pd.Series(res)


#   查看需下载的主力合约起始结束日期
def main_start_end_download(code):
    res = swap_date(code)
    from datetime import timedelta, datetime
    result = []
    for i, v in enumerate(res):
        if i == 0:
            continue
        start = (res.index[i] - timedelta(7)).strftime('%Y-%m-%d')
        if i != len(res) - 1:
            end = (res.index[i + 1] + timedelta(7)).strftime('%Y-%m-%d')
        else:
            end = datetime.today().date().strftime('%Y-%m-%d')
        if v[:2] in ['RB', 'AU', 'AG', 'RU']:
            v += '.SHF'
        elif v[:2] in ['RM', 'TA']:
            v += '.CZC'
        elif v[:1] == 'M':
            v += '.DCE'
        result.append((v, start, end))
    return result
