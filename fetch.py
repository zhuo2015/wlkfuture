import sys

sys.path.append('C:/Tinysoft/Analyse.NET')
import TSLPy3 as ty
from datetime import datetime, timedelta
import pandas as pd

_FUTURE_DAILY_DATA_LOCATION = "D:/Data/Futures/Daily/"
_FUTURE_MINUTE_DATA_LOCATION = "D:/Data/Futures/Minute/"

_NOW_TIME = datetime.today().replace(hour=15, minute=35, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
_NOW_DAY = str((datetime.today() - timedelta(1)).date())
_WIND_CODE = {'RB': '.SHF', 'RM': '.CZC', 'AU': '.SHF', 'AG': '.SHF', 'CU': '.SHF', 'TA': '.CZC', 'M': '.DCE',
              'I': '.DCE', 'PB': '.SHF', 'ZN': '.SHF'}
main_contract = {'au': 'ZL000002', 'cu': 'ZL000003', 'ru': 'ZL000005', 'cf': 'ZL000007', 'm': 'ZL000018',
                 'rb': 'ZL000023', 'zl': 'ZL000028',
                 'rm': 'ZL000031', 'i': 'ZL000034', 'p': 'ZL000019', 'bu': 'ZL000033'}

S1 = b'\xb3\xc9\xbd\xbb\xbd\xf0\xb6\xee'
S2 = b'\xb3\xc9\xbd\xbb\xc1\xbf'
S3 = b'\xb3\xd6\xb2\xd6\xc1\xbf'
S4 = b'\xbf\xaa\xc5\xcc\xbc\xdb'
S5 = b'\xca\xb1\xbc\xe4'
S6 = b'\xca\xd5\xc5\xcc\xbc\xdb'
S7 = b'\xd7\xee\xb5\xcd\xbc\xdb'
S8 = b'\xd7\xee\xb8\xdf\xbc\xdb'
S9 = b'\xbd\xe1\xcb\xe3\xbc\xdb'
_NAME = {S1: 'amt', S2: 'volume', S3: 'position', S4: 'open', S5: 'date', S6: 'close', S7: 'low', S8: 'high',
         S9: 'settle'}


# get future data from tinysoft
def future_minute_from_tinysoft(code, freq):
    begt = ty.EncodeDate(2010, 1, 1)
    year = int(_NOW_DAY[:4])
    mon = int(_NOW_DAY[5:7])
    day = int(_NOW_DAY[8:10])
    endt = ty.EncodeDate(year, mon, day)
    if freq in [1, 5, 15, 30, 60]:
        cy = '%d分钟线' % freq
    else:
        raise ValueError('freq must be 1,5,15,30,60')
    res = ty.RemoteCallFunc("getData", [code, begt, endt, cy], {})[1]
    df = pd.DataFrame(res)
    df = df.rename(columns=_NAME)
    df = df.reindex(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amt', 'position'])
    df.date = df.date.apply(lambda x: x.decode('utf-8'))
    df.set_index('date', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    return df


# get future data from tinysoft
def future_daily_from_tinysoft(code):
    begt = ty.EncodeDate(2010, 1, 1)
    year = int(_NOW_DAY[:4])
    mon = int(_NOW_DAY[5:7])
    day = int(_NOW_DAY[8:10])
    endt = ty.EncodeDate(year, mon, day)
    res = ty.RemoteCallFunc("getDaily", [code, begt, endt], {})[1]
    df = pd.DataFrame(res)
    df = df.rename(columns=_NAME)
    df = df.reindex(columns=['date', 'open', 'high', 'low', 'close', 'settle', 'volume', 'amt', 'position'])
    df.date = df.date.apply(lambda x: x.decode('utf-8'))
    df.set_index('date', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    return df


#   get future data from wind
def future_minute_from_wind(code, start='2010-01-01', end=_NOW_TIME, freq=15):
    from WindPy import w
    w.start()
    code += _WIND_CODE[code]
    start += " 09:00:00"
    end += " 15:00:00"

    if freq not in [1, 5, 15, 30, 60]:
        raise ValueError('frequency must be 1、5、15、30、60')
    else:
        freq = "BarSize=%d" % freq
    ds = w.wsi(code, "open,high,low,close,volume,amt,oi", start, end, freq)
    if ds.ErrorCode == 0:
        ds.Times = pd.DatetimeIndex([x.replace(microsecond=0) for x in ds.Times])
        ds = pd.DataFrame(ds.Data, index=ds.Fields, columns=ds.Times).T
        ds.columns = [x.lower() for x in ds.columns]
        ds = ds[ds.any(1)]
        ds = ds.applymap(lambda x: float(x))
        return ds


# w.wsd("AG1612.SHF","open,high,low,close,settle,volume,amt,oi","2016-04-20","2016-07-25")
def future_daily_from_wind(code, start, end=_NOW_DAY):
    from WindPy import w
    w.start()
    code += _WIND_CODE[code]
    ds = w.wsd(code, "open,high,low,close,settle,volume,amt,oi", start, end)
    if ds.ErrorCode == 0:
        ds.Times = pd.DatetimeIndex([x.date() for x in ds.Times])
        ds = pd.DataFrame(ds.Data, index=ds.Fields, columns=ds.Times).T
        ds.columns = [x.lower() for x in ds.columns]
        ds = ds[ds.any(1)]
        ds = ds.applymap(lambda x: float(x))
        return ds


# 获取期货分钟数据
def future_minute(code, freq):
    import os
    code = code.lower()
    file_name = _FUTURE_MINUTE_DATA_LOCATION + str(freq) + "/" + code + ".csv"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, index_col=0, parse_dates=True)
        return df
    else:
        print('no local csv file')


# 获取期货主连日度数据
def future_daily(code):
    import os
    code = code.lower()
    file_name = _FUTURE_DAILY_DATA_LOCATION + code + ".csv"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, index_col=0, parse_dates=True)
        return df
    else:
        print('no local csv file')


# 更新日度数据至最新
def update_daily(code):
    df = future_daily(code)
    if df is None:
        return
    start = str(df.index[-1].date())
    ds = future_daily_from_wind(code, start=start)
    res = pd.concat([df, ds])
    res = res.drop_duplicates()[:-1]
    res = res.applymap(lambda x: float(x))
    res.to_csv(_FUTURE_DAILY_DATA_LOCATION + code + '.csv')
    return res
