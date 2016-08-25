import TSLPy3 as ty
from .variables import *


# get future minute data from tinysoft
def future_minute_from_tinysoft(code, beg=None, end=None, freq=5):
    import pandas as pd
    begt, endt = _tydate(beg, end)
    if freq in [1, 5, 15, 30, 60]:
        cy = '%d分钟线' % freq
    else:
        raise ValueError('freq must be 1,5,15,30,60')
    res = ty.RemoteCallFunc("getDetail", [code, begt, endt, cy], {})[1]
    df = pd.DataFrame(res)
    df = df.rename(columns=FU_NAME_1)
    df = df.reindex(columns=MINUTE_COL_2)
    df.date = df.date.apply(lambda x: x.decode('utf-8'))
    df.set_index('date', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _tydate(beg=None, end=None):
    from dateutil import parser
    beg = parser.parse(beg)
    end = parser.parse(end)
    if beg:
        begt = ty.EncodeDate(beg.year, beg.month, beg.day)
    else:
        begt = ty.EncodeDate(2016, 1, 1)
    if end:
        endt = ty.EncodeDate(end.year, end.month, end.day)
    else:
        year = int(END_DAY[:4])
        mon = int(END_DAY[5:7])
        day = int(END_DAY[8:10])
        endt = ty.EncodeDate(year, mon, day)
    return begt, endt


# get future minute data from tinysoft
def stock_from_tinysoft(code, beg=None, end=None, freq='日线'):
    import pandas as pd
    begt, endt = _tydate(beg, end)
    if freq in [1, 2, 3, 5, 10, 15, 20, 30, 40, 60, 120]:
        cy = '%d分钟线' % freq
    else:
        cy = freq
    res = ty.RemoteCallFunc("stockData", [code, begt, endt, cy], {})[1]
    df = pd.DataFrame(res)
    df.columns = df.columns.map(lambda x: x.decode('utf-8'))
    df = df.reindex(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
    df.date = df.date.apply(lambda x: x.decode('utf-8'))
    df.set_index('date', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    return df


# get future daily data from tinysoft
def future_daily_from_tinysoft(code):
    import pandas as pd
    begt = ty.EncodeDate(2008, 1, 1)
    year = int(END_DAY[:4])
    mon = int(END_DAY[5:7])
    day = int(END_DAY[8:10])
    endt = ty.EncodeDate(year, mon, day)
    res = ty.RemoteCallFunc("dailyData", [code, begt, endt], {})[1]
    df = pd.DataFrame(res)
    df = df.rename(columns=FU_NAME_1)
    df = df.reindex(columns=DAILY_COL)
    df.date = df.date.apply(lambda x: x.decode('utf-8'))
    df.set_index('date', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    return df


# get future main_contract swap information from tinysoft
def future_swap_from_tinysoft(code):
    import pandas as pd
    res = ty.RemoteCallFunc("getMainCon", [code], {})[1]
    df = pd.DataFrame(res)
    df = df.ix[:, -1].ix[0]
    df = pd.DataFrame(df)
    df = df.rename(columns=FU_NAME_2)
    df = df.ix[1:, [0, 2, 3]]
    df['code'] = df['code'].apply(lambda x: x.decode('utf-8'))
    df['month'] = df['month'].apply(lambda x: x.decode('utf-8'))
    df = df.set_index('date')
    return df


# 下载主力连续合约数据到本地csv
def download_all_zl_data():
    import os
    for name, code in MAIN_CONTRACT.items():
        file_name = FUTURE_DAILY_DATA_LOCATION + name + '_zl.csv'
        if not os.path.exists(file_name):
            df = future_daily_from_tinysoft(code)
            if len(df) == 0:
                continue
            df.to_csv(file_name)


# 下载所有合约历史日频数据到本地csv
def download_all_history_daily_data():
    import os
    for code in CODES:
        file_name = FUTURE_DAILY_DATA_LOCATION + code + '.csv'
        if not os.path.exists(file_name):
            df = future_daily_from_tinysoft(code)
            if len(df) == 0:
                continue
            df.to_csv(file_name)


# 下载所有合约历史分钟数据到本地csv
def download_all_history_minute_data():
    import os
    for code in CODES:
        for minu in [1, 5]:
            file_name = FUTURE_MINUTE_DATA_LOCATION + str(minu) + '/' + code + '.csv'
            if not os.path.exists(file_name):
                df = future_minute_from_tinysoft(code, minu)
                if len(df) == 0:
                    break
                df.to_csv(file_name)


# 下载历史所有合约主力换月信息
def download_all_swap_info():
    loc = 'D:/Data/Futures/'
    for name, code in MAIN_CONTRACT.items():
        df = future_swap_from_tinysoft(code)
        if len(df) == 0:
            continue
        df.to_csv(loc + name + '_swap.csv')

# # 更新日度数据至最新
# def update_daily(code):
#     df = future_daily(code)
#     if df is None:
#         return
#     start = str(df.index[-1].date())
#     ds = future_daily_from_wind(code, start=start)
#     res = pd.concat([df, ds])
#     res = res.drop_duplicates()[:-1]
#     res = res.applymap(lambda x: float(x))
#     res.to_csv(_FUTURE_DAILY_DATA_LOCATION + code + '.csv')
#     return res
