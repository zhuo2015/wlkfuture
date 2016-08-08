# encoding = utf-8
from datetime import datetime
import pandas as pd

_FUTURE_DAILY_DATA_LOCATION = "D:/Data/Futures/"
_FUTURE_MINUTE_DATA_LOCATION = "D:/Data/Futures/Minute/"

_NOW = datetime.today().replace(hour=15, minute=35, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


#   get future data from wind
def future_minute_from_wind(code, start, end=_NOW, freq=15):
    from WindPy import w
    w.start()
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


# get future data from wind
#   w.wsd("AG1612.SHF","open,high,low,close,settle,volume,amt,oi","2016-04-20","2016-07-25")
def future_daily_from_wind(code, start, end):
    from WindPy import w
    w.start()
    ds = w.wsd(code, "open,high,low,close,settle,volume,amt,oi", start, end)
    if ds.ErrorCode == 0:
        ds.Times = pd.DatetimeIndex([x.date() for x in ds.Times])
        ds = pd.DataFrame(ds.Data, index=ds.Fields, columns=ds.Times).T
        ds.columns = [x.lower() for x in ds.columns]
        ds = ds[ds.any(1)]
        ds = ds.applymap(lambda x: float(x))
        return ds


# 获取期货分钟数据
def future_minute(code, start, freq):
    import os
    code = code.upper()
    file_name = _FUTURE_MINUTE_DATA_LOCATION + str(freq) + "/" + code + ".csv"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, index_col=0, parse_dates=True)
        # df = df.applymap(lambda x: float(x))
        return df
    else:
        print('no local csv file')


# 获取期货主连日度数据
def future_daily(code):
    import os
    code = code.upper()
    file_name_1 = _FUTURE_DAILY_DATA_LOCATION + 'Main_Con/' + code + ".csv"
    file_name_2 = _FUTURE_DAILY_DATA_LOCATION + 'Daily/' + code + '.csv'
    if os.path.exists(file_name_1):
        df = pd.read_csv(file_name_1, index_col=0, parse_dates=True)
        return df
    elif os.path.exists(file_name_2):
        df = pd.read_csv(file_name_2, index_col=0, parse_dates=True)
        return df
    else:
        print('no local csv file')
