#   查找每个合约的主力合约日期
def swap_date(code):
    import pandas as pd
    df = pd.read_csv('D:/Data/Futures/%s' % code + '_swap.csv')
    df['date'] = df['date'].apply(lambda x: str(x))
    from datetime import datetime, timedelta
    from dateutil.parser import parse
    now = datetime.today().date()
    res = {}
    for i, v in enumerate(df.code):
        if i != len(df) - 1:
            res[v] = [parse(df.date[i]).date() + timedelta(1), parse(df.date[i + 1]).date()]
        else:
            res[v] = [parse(df.date[i]).date() + timedelta(1), now]
    return res


#   查找每个合约的主力合约日期
def swap_date_bt(code):
    import pandas as pd
    df = pd.read_csv('D:/Data/Futures/%s' % code + '_swap.csv')
    df['date'] = df['date'].apply(lambda x: str(x))
    from datetime import datetime, timedelta
    from dateutil.parser import parse
    now = datetime.today().replace(hour=15, minute=0, second=0, microsecond=0)
    res = {}
    for i, v in enumerate(df.code):
        begt = parse(df.date[i]) + timedelta(1)
        begt = begt.replace(hour=15)
        if i != len(df) - 1:
            endt = parse(df.date[i + 1]).replace(hour=15)
            res[v] = [begt, endt]
        else:
            res[v] = [begt, now]
    return res


#   生成考虑了换月情况的主力连续回测数据
def generate_swap_zl(code, minute=None):
    import pandas as pd
    res = swap_date(code)
    files = sorted(res.keys())[1:]
    local = 'D:/Data/Futures/Minute/%d' % minute + '/' if minute is not None else 'D:/Data/Futures/Daily/'
    result = []
    for f in files:
        try:
            df = pd.read_csv(local + f + '.csv', index_col=0, parse_dates=True)
        except OSError:
            continue
        beg, end = res[f]
        end = end.strftime('%Y-%m-%d')
        df = df.ix[beg:end]
        if minute is not None:
            df = df.between_time('8:50', '15:50')
        result.append(df)
    data = pd.concat(result)
    df = data.sort_index()
    return df


#   生成考虑了换月情况的主力连续回测数据
def generate_swap_zl_signal(code, indicator, minute=5, **kwargs):
    import pandas as pd
    res = swap_date(code)
    sds = []
    files = sorted(res.keys())
    local = 'D:/Data/Futures/Minute/%d' % minute + '/' if minute is not None else 'D:/Data/Futures/Daily/'
    result = []
    for f in files:
        try:
            df = pd.read_csv(local + f + '.csv', index_col=0, parse_dates=True)
            df = indicator(df, **kwargs)
        except OSError:
            continue
        beg, end = res[f]
        sds.append(end)
        end = end.strftime('%Y-%m-%d')
        df = df.ix[beg:end]
        df = df.between_time('8:50', '15:50')
        result.append(df)
    data = pd.concat(result).dropna()
    df = data.sort_index()
    return df, sds


def _actual_signal(data):
    data['signal'] = 0
    hold = 0
    state = None
    for now in data.index:
        df = data.ix[now]
        l_s = df['long_signal']
        s_s = df['short_signal']
        if hold == 0:
            if l_s == 1:
                data.at[now, 'signal'] = 1  # 多开
                hold = 1
                state = 'long'
            elif s_s == 1:
                data.at[now, 'signal'] = 2  # 空开
                hold = 1
                state = 'short'
        elif hold == 1:
            if state == 'short' and s_s == -1:
                data.at[now, 'signal'] = -2  # 空平
                state = None
                hold = 0
            elif state == 'long' and l_s == -1:
                data.at[now, 'signal'] = -1  # 多平
                state = None
                hold = 0
    return data
