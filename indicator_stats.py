import pandas as pd
import numpy as np

_FUTURE_DAYS = np.array([1, 3, 5, 7, 10, 15, 20, 30, 50])


# 将 1、-1替换为多空
def _replace_signal(lst):
    res = []
    for i in range(0, len(lst), 2):
        if lst[i] == 1:
            res.append('long open')
            res.append('long close')
        else:
            res.append('short open')
            res.append('short close')
    return res[:len(lst)]


#   获取实际交易信号
def actual_signal(df):
    sigs = df.signal[df.signal.notnull()]
    res_index = []
    res_state = []
    for i in range(len(sigs)):
        if i == 0:
            res_index.append(sigs.index[0])
            res_state.append(sigs[0])
            continue
        # 获取最新的状态
        if len(res_state) % 2 != 0:
            state = res_state[-1]
        else:
            res_index.append(sigs.index[i])
            res_state.append(sigs[i])
            continue
        if sigs[i] == -state:
            res_index.append(sigs.index[i])
            res_state.append(sigs[i])
    _state = _replace_signal(res_state)
    _signals = pd.Series(_state, index=res_index)
    _df = pd.concat([df.close, _signals], axis=1)
    _df = _df.fillna(0)
    _df.columns = ['close', 'signal']
    return _df


#  未来N日内收益
def look_forward_return(data):
    _func = lambda x: data.close.pct_change(x).shift(-x)
    lst = list(map(_func, _FUTURE_DAYS))
    col_name = ["%d_day" % x for x in _FUTURE_DAYS]
    df = pd.concat(lst, axis=1)
    df.columns = col_name
    return df


#   查看信号及其后收益
def signal_returns_stats(data):
    returns = look_forward_return(data)
    sig = data[data.signal != 0].dropna()
    _df = pd.concat([sig, returns], axis=1, join='inner')
    return _df


#   各收益率占比
def returns_ratio(df):
    '''
    Parameters
    ----------
    df:收益率序列,series
    '''
    dd = {}
    n = len(df)
    dd['15%'] = len(df[df > 0.15]) / n
    dd['10%'] = len(df[df > 0.1]) / n
    dd['7%'] = len(df[df > 0.07]) / n
    dd['5%'] = len(df[df > 0.05]) / n
    dd['3%'] = len(df[df > 0.03]) / n
    dd['1%'] = len(df[df > 0.01]) / n
    dd['-1%'] = len(df[df < -0.01]) / n
    dd['-3%'] = len(df[df < -0.03]) / n
    dd['-5%'] = len(df[df < -0.05]) / n
    dd['-7%'] = len(df[df < -0.07]) / n
    dd['-10%'] = len(df[df < -0.1]) / n
    dd['-15%'] = len(df[df < -0.15]) / n
    y = ['15%', '10%', '7%', '5%', '3%', '1%', '-1%', '-3%', '-5%', '-7%', '-10%', '-15%']
    return pd.Series(dd).reindex(y)


#   对称收益率之差占比
def excel_eturns_ratio(df, plus=1):
    '''
    Parameters
    ----------
    df:收益率序列,series
    '''
    dd = {}
    n = len(df)
    dd['+-15%'] = (len(df[df > 0.15]) - len(df[df < -0.15])) / n
    dd['+-10%'] = (len(df[df > 0.1]) - len(df[df < -0.1])) / n
    dd['+-7%'] = (len(df[df > 0.07]) - len(df[df < -0.07])) / n
    dd['+-5%'] = (len(df[df > 0.05]) - len(df[df < -0.05])) / n
    dd['+-3%'] = (len(df[df > 0.03]) - len(df[df < -0.03])) / n
    dd['+-1%'] = (len(df[df > 0.01]) - len(df[df < -0.01])) / n
    y = ['+-15%', '+-10%', '+-7%', '+-5%', '+-3%', '+-1%']
    df = pd.Series(dd).reindex(y)
    if plus == 1:
        return df
    elif plus == -1:
        return -df


# 信号收益分析
def signal_stats(df, state=1):
    dd = dict()
    plus = df[df > 0]
    minus = df[df < 0]
    dd['count'] = len(df)
    dd['plus_count'] = len(plus)
    dd['minus_count'] = len(minus)
    dd['mean_return'] = df.mean()
    if state == 1:
        dd['accurate_mean'] = plus.mean()
        dd['wrong_mean'] = minus.mean()
        dd['accurate_ratio'] = len(plus) / len(df)  # if minus!=0 else 'all plus'
        dd['max_return_accurate'] = plus.max()
        dd['max_return_wrong'] = minus.min()
    elif state == -1:
        dd['accurate_mean'] = minus.mean()
        dd['wrong_mean'] = plus.mean()
        dd['accurate_ratio'] = len(minus) / len(df)  # if plus!=0 else 'all minus'
        dd['max_return_accurate'] = minus.min()
        dd['max_return_wrong'] = plus.max()
    s = pd.Series(dd)
    y = ['count', 'plus_count', 'minus_count', 'accurate_ratio', 'mean_return', 'accurate_mean', 'wrong_mean', \
         'max_return_accurate', 'max_return_wrong']
    return s.reindex(y)
