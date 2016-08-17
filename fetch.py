import pandas as pd

_FUTURE_DAILY_DATA_LOCATION = "D:/Data/Futures/Daily/"
_FUTURE_MINUTE_DATA_LOCATION = "D:/Data/Futures/Minute/"


#   获取期货分钟数据
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
