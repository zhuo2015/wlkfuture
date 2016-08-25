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


#   生成考虑了换月情况、夜盘数据的主力连续回测数据
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


#   生成考虑了换月情况、非夜盘数据的主力连续回测数据
def generate_swap_zl_signal2(code, indicator, minute=5, **kwargs):
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
        result.append(df)
    data = pd.concat(result).dropna()
    df = data.sort_index()
    return df, sds


#   生成换月后按信号平仓的主力连续回测数据
def generate_rb_zl_signal(indicator, minute=5, **kwargs):
    import pandas as pd
    res = swap_date('rb')
    files = sorted(res.keys())
    local = 'D:/Data/Futures/Minute/%d' % minute + '/' if minute is not None else 'D:/Data/Futures/Daily/'
    result = []
    begt = None
    for i, f in enumerate(files):
        df = pd.read_csv(local + f + '.csv', index_col=0, parse_dates=True)
        df = df.between_time('8:50', '15:50')
        df = indicator(df, **kwargs)
        if i == 0:
            df, beg = _actual_signal(df, res[f][0], res[f][1])
            begt = beg
        elif i == len(files) - 1:
            df = _actual_signal(df, res[f][0], res[f][1], True)
            df = df.ix[begt:]
        else:
            df, beg = _actual_signal(df, begt, res[f][1])
            begt = beg
        result.append(df)
    data = pd.concat(result)  # .dropna()
    data = data[['close', 'ex_price', 'open', 'signal']]
    data = data.sort_index()
    data = pd.Panel({'RB': data})
    return data


#   生成换月后按信号平仓的主力连续回测数据
def generate_signal_swap(code, indicator, minute=5, night=False, **kwargs):
    import pandas as pd
    res = swap_date(code)
    files = sorted(res.keys())
    local = 'D:/Data/Futures/Minute/%d' % minute + '/' if minute is not None else 'D:/Data/Futures/Daily/'
    result = []
    begt = None
    for i, f in enumerate(files):
        df = pd.read_csv(local + f + '.csv', index_col=0, parse_dates=True)
        if night:
            df['signal'] = indicator(df, **kwargs)['signal']
            df = df.between_time('8:50', '15:50')
        else:
            df = df.between_time('8:50', '15:50')
            df['signal'] = indicator(df, **kwargs)['signal']

        if i == 0:
            df = df[res[f][0]:]
            df, beg = indicator_actual_signal(df, swapt=res[f][1])
            # print(f, res[f][0], beg)
            begt = beg
        elif i == len(files) - 1:
            df = df[begt:]
            # print(f, begt)
            df = indicator_actual_signal(df, flag=True)
        else:
            # 如果起始时间小于换月时间，跳过该合约
            if begt > res[f][1]:
                continue

            df = df[begt:]
            df, beg = indicator_actual_signal(df, swapt=res[f][1])
            # print(f, begt, beg)
            begt = beg
        result.append(df)
    data = pd.concat(result)
    data = data.sort_index()
    data['n_open'] = data.open.shift(1)
    data['buy'] = data[['sell1', 'n_open']].max(1)
    data['sell'] = data[['buy1', 'n_open']].min(1)
    return data[['close', 'open', 'real_signal', 'buy', 'sell']]


#   按指标平仓信号换月,swap:datetime.date
def indicator_actual_signal(data, swapt=None, flag=False):
    from datetime import timedelta
    df_sig = data.copy()
    df = df_sig[(df_sig.signal == 1) | (df_sig.signal == -1)]
    df_sig['real_signal'] = 0
    hold = False
    state = None
    for idx, sig in enumerate(df.signal):
        if not hold:
            state = sig
            df_sig.at[df.index[idx], 'real_signal'] = sig
            hold = True
        elif hold:
            if sig == state:
                continue
            else:
                df_sig.at[df.index[idx], 'real_signal'] = sig
                state = None
                hold = False
    if flag:
        return df_sig

    x = df_sig[(df_sig.real_signal == 1) | (df_sig.real_signal == -1)]
    nums = len(x[:str(swapt)])
    if nums % 2 == 0:
        endt = swapt
    else:
        # 换月后无平仓信号
        if len(x) == nums:
            endt = swapt + timedelta(25)
            # 换月后25天自动平仓
            t = df_sig[:str(endt)].index[-2]
            df_sig.at[t, 'real_signal'] = -x.ix[nums - 1, 'real_signal']
        else:
            df = x.ix[nums:]
            if len(df) != 1:
                df_sig.ix[df.index[1]:, 'real_signal'] = 0
            endt = df.index[0].date()
    start = endt + timedelta(1)
    return df_sig.ix[:str(endt)], start


def _actual_signal(data, beg, swapt, flag=False):  # datetime.date
    from datetime import timedelta
    data['signal'] = 0
    hold = 0
    state = None
    idx = data[(data.long_signal != 0) | (data.short_signal != 0)].index
    for now in idx:
        l_s = data.at[now, 'long_signal']
        s_s = data.at[now, 'short_signal']
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
    if flag:
        return data
    ds = data.ix[swapt:].ix[data.signal != 0]  # 换月日后的信号
    if len(ds) > 1:
        data.ix[ds.index[1]:, 'signal'] = 0
    if len(ds) == 0:
        end = swapt
    else:
        end = ds.index[0].date() if ds.iat[0, -1] < 0 else swapt
    start = end + timedelta(1)
    return data[str(beg):str(end)], start
