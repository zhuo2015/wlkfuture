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
            if minute is not None:
                df = df.between_time('8:50', '15:50')
        except OSError:
            continue
        beg, end = res[f]
        end = end.strftime('%Y-%m-%d')
        df = df.ix[beg:end]
        result.append(df)
    data = pd.concat(result)
    df = data.sort_index()
    return df


#
# #   生成考虑了换月情况、夜盘数据的主力连续回测数据
# def generate_dualthrust_swap(code, indicator, minute=5, **kwargs):
#     import pandas as pd
#     res = swap_date(code)
#     sds = []
#     files = sorted(res.keys())
#     local = 'D:/Data/Futures/Minute/%d' % minute + '/' if minute is not None else 'D:/Data/Futures/Daily/'
#     result = []
#     for f in files:
#         try:
#             df = pd.read_csv(local + f + '.csv', index_col=0, parse_dates=True)
#             df = indicator(df, **kwargs)
#         except OSError:
#             continue
#         beg, end = res[f]
#         sds.append(end)
#         end = end.strftime('%Y-%m-%d')
#         df = df.ix[beg:end]
#         df = df.between_time('8:50', '15:50')
#         result.append(df)
#     data = pd.concat(result).dropna()
#     df = data.sort_index()
#     return df, sds


#   生成换月后按信号平仓的主力连续回测数据
def generate_signal_swap(code, indicator, minute=None, night=False, **kwargs):
    import pandas as pd
    import numpy as np
    res = swap_date(code)
    files = sorted(res.keys())
    local = 'D:/Data/Futures/Minute/%d' % minute + '/' if minute is not None else 'D:/Data/Futures/Daily/'
    result = []
    begt = None
    for i, f in enumerate(files):
        try:
            df = pd.read_csv(local + f + '.csv', index_col=0, parse_dates=True)
        except:
            continue
        if night:
            df['signal'] = indicator(df, **kwargs)['signal']
            if minute:
                df = df.between_time('8:50', '15:50').copy()
                df['n_open'] = df['open'].shift(-1)
        else:
            if minute:
                df = df.between_time('8:50', '15:50')
                df['n_open'] = df.open.shift(-1).copy()
            df['signal'] = indicator(df, **kwargs)['signal']

        if i == 0:
            df = df[res[f][0]:]
            df, beg = indicator_actual_signal(df, swapt=res[f][1])
            begt = beg
        elif i == len(files) - 1:
            df = df[begt:]
            df = indicator_actual_signal(df, flag=True)
        else:
            # 如果起始时间小于换月时间，跳过该合约
            if begt > res[f][1]:
                continue

            df = df[begt:]
            df, beg = indicator_actual_signal(df, swapt=res[f][1])
            begt = beg
        result.append(df)
    data = pd.concat(result)
    data = data.sort_index()
    if minute:
        data.ix[data.at_time('15:00').index, 'n_open'] = np.nan
        data['buy'] = data[['sell1', 'n_open']].max(1)
        data['sell'] = data[['buy1', 'n_open']].min(1)
        return data[['close', 'open', 'real_signal', 'buy', 'sell']]
    else:
        return data[['close', 'settle', 'open', 'real_signal']]


# 按指标平仓信号换月,swap:datetime.date
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
