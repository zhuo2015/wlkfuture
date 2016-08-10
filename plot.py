# encoding = utf-8
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.rcParams['savefig.dpi'] = 1.2 * plt.rcParams['savefig.dpi']


#   净值曲线
def plot_equity_curve(portfolio):
    portfolio.plot(label='Strategy', figsize=(15, 6.5))
    plt.xlabel('Backtest period', fontsize=12, color='k')
    plt.ylabel('Portfolio Value', fontsize=12, color='k')
    plt.show()


#   持仓市值曲线
def plot_hold_values(strategy):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6
    nums = len(strategy.items)
    f, axes = plt.subplots(nums, figsize=(dxs, dys * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]
        long_open = (x.state == 'open') & (x.long_short == 'long')
        short_open = (x.state == 'open') & (x.long_short == 'short')
        long_close = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'long')
        short_close = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'short')
        item = 'hold_value'
        if nums == 1:
            axes.plot(x.index, x[item], c='k')
            axes.plot(x[long_open].index, x[long_open][item], '^', markersize='7', c='r', label='long_open')
            axes.plot(x[long_close].index, x[long_close][item], 'v', markersize='7', c='g', label='long_close')
            axes.plot(x[short_open].index, x[short_open][item], '^', markersize='7', c='b', label='short_open')
            axes.plot(x[short_close].index, x[short_close][item], 'v', markersize='7', c='y', label='short_close')
            axes.set_xlabel(sec, fontsize=13, color='k')
            axes.set_ylabel('Hold Value', fontsize=13, color='k')
            axes.legend(loc='best', fontsize=10)
        else:
            axes[i].plot(x.index, x[item], c='k')
            axes[i].plot(x[long_open].index, x[long_open][item], '^', markersize='7', c='r', label='long_open')
            axes[i].plot(x[long_close].index, x[long_close][item], 'v', markersize='7', c='g', label='long_close')
            axes[i].plot(x[short_open].index, x[short_open][item], '^', markersize='7', c='b', label='short_open')
            axes[i].plot(x[short_close].index, x[short_close][item], 'v', markersize='7', c='y', label='short_close')
            axes[i].set_xlabel(sec, fontsize=13, color='k')
            axes[i].set_ylabel('Hold Value', fontsize=13, color='k')
            axes[i].legend(loc='best', fontsize=10)
    if nums != 1:
        f.subplots_adjust(hspace=0.2)


# 画出实际交易信号
def plot_all_old(strategy):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6.5
    nums = len(strategy.items)
    f, axes = plt.subplots(2 * nums, figsize=(dxs, dys * 2 * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]
        long_open = (x.state == 'open') & (x.long_short == 'long')
        short_open = (x.state == 'open') & (x.long_short == 'short')
        long_close = (x.state == 'close') & (x.long_short == 'long')
        short_close = (x.state == 'close') & (x.long_short == 'short')
        long_close_ = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'long')
        short_close_ = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'short')
        price = 'price'
        item = 'hold_value'
        axes[2 * i].plot(x.index, x[price], c='k')
        axes[2 * i].plot(x[long_open].index, x[long_open][price], '^', markersize='7', c='r', label='long_open')
        axes[2 * i].plot(x[long_close].index, x[long_close][price], 'v', markersize='7', c='g', label='long_close')
        axes[2 * i].plot(x[short_open].index, x[short_open][price], '^', markersize='7', c='b', label='short_open')
        axes[2 * i].plot(x[short_close].index, x[short_close][price], 'v', markersize='7', c='y',
                         label='short_close')
        axes[2 * i].set_xlabel(sec, fontsize=13, color='k')
        axes[2 * i].set_ylabel('Settle Price', fontsize=15, color='k')
        axes[2 * i].legend(loc='best', fontsize=12)
        axes[2 * i + 1].plot(x.index, x[item], c='k')
        axes[2 * i + 1].plot(x[long_open].index, x[long_open][item], '^', markersize='7', c='r', label='long_open')
        axes[2 * i + 1].plot(x[long_close_].index, x[long_close_][item], 'v', markersize='7', c='g',
                             label='long_close')
        axes[2 * i + 1].plot(x[short_open].index, x[short_open][item], '^', markersize='7', c='b',
                             label='short_open')
        axes[2 * i + 1].plot(x[short_close_].index, x[short_close_][item], 'v', markersize='7', c='y',
                             label='short_close')
        axes[2 * i + 1].set_xlabel(sec, fontsize=13, color='k')
        axes[2 * i + 1].set_ylabel('Hold Value', fontsize=13, color='k')
        axes[2 * i + 1].legend(loc='best', fontsize=10)
    f.subplots_adjust(hspace=0.2)


def plot_all_new(strategy, tlog):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6.5
    nums = len(strategy.items)
    f, axes = plt.subplots(2 * nums, figsize=(dxs, dys * 2 * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]['price']
        z = strategy[sec]['hold_value']
        y = tlog[tlog.security == sec]
        l_o = [t for t in y[(y.direction == 'open') & (y.long_short == 'long')].index]
        _l_o = [x.date() for x in l_o]
        s_o = [t for t in y[(y.direction == 'open') & (y.long_short == 'short')].index]
        _s_o = [x.date() for x in s_o]
        l_c = [t for t in y[(y.direction == 'close') & (y.long_short == 'long')].index]
        _l_c = [x.date() for x in l_c]
        s_c = [t for t in y[(y.direction == 'close') & (y.long_short == 'short')].index]
        _s_c = [x.date() for x in s_c]
        axes[2 * i].plot(x.index, x, c='k')
        axes[2 * i].plot(_l_o, y.ix[l_o].price, '^', markersize='7', c='r', label='long_open')
        axes[2 * i].plot(_s_o, y.ix[s_o].price, '^', markersize='7', c='b', label='short_open')
        axes[2 * i].plot(_l_c, y.ix[l_c].price, 'v', markersize='7', c='g', label='long_close')
        axes[2 * i].plot(_s_c, y.ix[s_c].price, 'v', markersize='7', c='y', label='short_close')
        axes[2 * i].set_xlabel(sec, fontsize=13, color='k')
        axes[2 * i].set_ylabel('Price', fontsize=15, color='k')
        axes[2 * i].legend(loc='best', fontsize=11)
        #
        axes[2 * i + 1].plot(z.index, z, c='k')
        axes[2 * i + 1].plot(_l_o, z.ix[_l_o], '^', markersize='7', c='r', label='long_open')
        axes[2 * i + 1].plot(_s_o, z.ix[_s_o], '^', markersize='7', c='b', label='short_open')
        axes[2 * i + 1].plot(_l_c, z.shift(1).ix[_l_c], 'v', markersize='7', c='g', label='long_close')
        axes[2 * i + 1].plot(_s_c, z.shift(1).ix[_s_c], 'v', markersize='7', c='y', label='short_close')
        axes[2 * i + 1].set_xlabel(sec, fontsize=13, color='k')
        axes[2 * i + 1].set_ylabel('Hold Value', fontsize=15, color='k')
        axes[2 * i + 1].legend(loc='best', fontsize=11)
    f.subplots_adjust(hspace=0.2)


# 画出实际交易信号
def plot_trades(strategy):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6
    nums = len(strategy.items)
    f, axes = plt.subplots(nums, figsize=(dxs, dys * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]
        long_open = (x.state == 'open') & (x.long_short == 'long')
        short_open = (x.state == 'open') & (x.long_short == 'short')
        long_close = (x.state == 'close') & (x.long_short == 'long')
        short_close = (x.state == 'close') & (x.long_short == 'short')
        price = 'price'
        if nums == 1:
            axes.plot(x.index, x[price], c='k')
            axes.plot(x[long_open].index, x[long_open][price], '^', markersize='7', c='r', label='long_open')
            axes.plot(x[long_close].index, x[long_close][price], 'v', markersize='7', c='g', label='long_close')
            axes.plot(x[short_open].index, x[short_open][price], '^', markersize='7', c='b', label='short_open')
            axes.plot(x[short_close].index, x[short_close][price], 'v', markersize='7', c='y', label='short_close')
            axes.set_xlabel(sec, fontsize=13, color='k')
            axes.set_ylabel('Settle Price', fontsize=15, color='k')
            axes.legend(loc='best', fontsize=12)
        else:
            axes[i].plot(x.index, x[price], c='k')
            axes[i].plot(x[long_open].index, x[long_open][price], '^', markersize='7', c='r', label='long_open')
            axes[i].plot(x[long_close].index, x[long_close][price], 'v', markersize='7', c='g', label='long_close')
            axes[i].plot(x[short_open].index, x[short_open][price], '^', markersize='7', c='b', label='short_open')
            axes[i].plot(x[short_close].index, x[short_close][price], 'v', markersize='7', c='y',
                         label='short_close')
            axes[i].set_xlabel(sec, fontsize=13, color='k')
            axes[i].set_ylabel('Settle Price', fontsize=15, color='k')
            axes[i].legend(loc='best', fontsize=12)
    if nums != 1:
        f.subplots_adjust(hspace=0.2)


# 展示买卖信号
def plot_signal(df):
    '''
    Parameters
    ----------
    df:signal series,include signal and close,pandas

    '''
    import pandas as pd
    import numpy as np
    _signal_type = pd.unique(df.signal.dropna())
    if np.in1d(_signal_type, [0, 1, -1]).all():
        df.close.plot(c='k', figsize=(15, 6))
        plt.plot(df[df.signal == 1].index, df[df.signal == 1].close, '^', markersize=6, c='r', label='buy')
        plt.plot(df[df.signal == -1].index, df[df.signal == -1].close, 'v', markersize=6, c='g', label='sell')
        plt.legend(loc='best')
        plt.show()
    else:
        df.close.plot(c='k', figsize=(12, 6.5))
        plt.plot(df[df.signal == 'long open'].index, df[df.signal == 'long open'].close, '^', markersize=6, c='r',
                 label='long open')
        plt.plot(df[df.signal == 'short open'].index, df[df.signal == 'short open'].close, '^', markersize=6, c='b',
                 label='short open')
        plt.plot(df[df.signal == 'long close'].index, df[df.signal == 'long close'].close, 'v', markersize=6, c='g',
                 label='long close')
        plt.plot(df[df.signal == 'short close'].index, df[df.signal == 'short close'].close, 'v', markersize=6, c='y',
                 label='short close')
        plt.legend(loc='best')
        plt.show()


# 展示买卖信号
def plot_signal_minute(df):
    df = df.copy()
    tdx = range(len(df))
    df['pos'] = tdx
    freq = int(len(df) / 20)
    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xticks(tdx[::freq])
    ax.plot(tdx, df.close.values, c='k')
    ax.plot(df[df.signal == 1].pos, df[df.signal == 1].close, "^", markersize=7, c='r', label='buy')
    ax.plot(df[df.signal == -1].pos, df[df.signal == -1].close, "v", markersize=7, c='g', label='sell')
    ax.set_xticklabels([x.to_pydatetime().date() for x in df.index][::freq], rotation=35, horizontalalignment='right',
                       color='k')
    ax.set_xlabel('Date', color='k', size=15)
    ax.set_ylabel('Price', color='k', size=15)
    plt.legend(loc='best')


# encoding = utf-8
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.rcParams['savefig.dpi'] = 1.2 * plt.rcParams['savefig.dpi']


#   净值曲线
def plot_equity_curve(portfolio):
    portfolio.plot(label='Strategy', figsize=(15, 6))
    plt.xlabel('Backtest period', fontsize=12, color='k')
    plt.ylabel('Portfolio Value', fontsize=12, color='k')
    plt.show()


#   持仓市值曲线
def plot_hold_values(strategy):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6
    nums = len(strategy.items)
    f, axes = plt.subplots(nums, figsize=(dxs, dys * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]
        long_open = (x.state == 'open') & (x.long_short == 'long')
        short_open = (x.state == 'open') & (x.long_short == 'short')
        long_close = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'long')
        short_close = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'short')
        item = 'hold_value'
        if nums == 1:
            axes.plot(x.index, x[item], c='k')
            axes.plot(x[long_open].index, x[long_open][item], '^', markersize='7', c='r', label='long_open')
            axes.plot(x[long_close].index, x[long_close][item], 'v', markersize='7', c='g', label='long_close')
            axes.plot(x[short_open].index, x[short_open][item], '^', markersize='7', c='b', label='short_open')
            axes.plot(x[short_close].index, x[short_close][item], 'v', markersize='7', c='y', label='short_close')
            axes.set_xlabel(sec, fontsize=13, color='k')
            axes.set_ylabel('Hold Value', fontsize=13, color='k')
            axes.legend(loc='best', fontsize=10)
        else:
            axes[i].plot(x.index, x[item], c='k')
            axes[i].plot(x[long_open].index, x[long_open][item], '^', markersize='7', c='r', label='long_open')
            axes[i].plot(x[long_close].index, x[long_close][item], 'v', markersize='7', c='g', label='long_close')
            axes[i].plot(x[short_open].index, x[short_open][item], '^', markersize='7', c='b', label='short_open')
            axes[i].plot(x[short_close].index, x[short_close][item], 'v', markersize='7', c='y', label='short_close')
            axes[i].set_xlabel(sec, fontsize=13, color='k')
            axes[i].set_ylabel('Hold Value', fontsize=13, color='k')
            axes[i].legend(loc='best', fontsize=10)
    if nums != 1:
        f.subplots_adjust(hspace=0.2)


# 画出实际交易信号
def plot_all(strategy):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6.5
    nums = len(strategy.items)
    f, axes = plt.subplots(2 * nums, figsize=(dxs, dys * 2 * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]
        long_open = (x.state == 'open') & (x.long_short == 'long')
        short_open = (x.state == 'open') & (x.long_short == 'short')
        long_close = (x.state == 'close') & (x.long_short == 'long')
        short_close = (x.state == 'close') & (x.long_short == 'short')
        long_close_ = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'long')
        short_close_ = (x.state.shift(-1) == 'close') & (x.long_short.shift(-1) == 'short')
        price = 'price'
        item = 'hold_value'
        axes[2 * i].plot(x.index, x[price], c='k')
        axes[2 * i].plot(x[long_open].index, x[long_open][price], '^', markersize='7', c='r', label='long_open')
        axes[2 * i].plot(x[long_close].index, x[long_close][price], 'v', markersize='7', c='g', label='long_close')
        axes[2 * i].plot(x[short_open].index, x[short_open][price], '^', markersize='7', c='b', label='short_open')
        axes[2 * i].plot(x[short_close].index, x[short_close][price], 'v', markersize='7', c='y',
                         label='short_close')
        axes[2 * i].set_xlabel(sec, fontsize=13, color='k')
        axes[2 * i].set_ylabel('Settle Price', fontsize=15, color='k')
        axes[2 * i].legend(loc='best', fontsize=12)
        axes[2 * i + 1].plot(x.index, x[item], c='k')
        axes[2 * i + 1].plot(x[long_open].index, x[long_open][item], '^', markersize='7', c='r', label='long_open')
        axes[2 * i + 1].plot(x[long_close_].index, x[long_close_][item], 'v', markersize='7', c='g',
                             label='long_close')
        axes[2 * i + 1].plot(x[short_open].index, x[short_open][item], '^', markersize='7', c='b',
                             label='short_open')
        axes[2 * i + 1].plot(x[short_close_].index, x[short_close_][item], 'v', markersize='7', c='y',
                             label='short_close')
        axes[2 * i + 1].set_xlabel(sec, fontsize=13, color='k')
        axes[2 * i + 1].set_ylabel('Hold Value', fontsize=13, color='k')
        axes[2 * i + 1].legend(loc='best', fontsize=10)
    f.subplots_adjust(hspace=0.2)


# 画出实际交易信号
def plot_trades(strategy):
    import matplotlib.pyplot as plt
    dxs = 15
    dys = 6
    nums = len(strategy.items)
    f, axes = plt.subplots(nums, figsize=(dxs, dys * nums))
    for i, sec in enumerate(strategy.items):
        x = strategy[sec]
        long_open = (x.state == 'open') & (x.long_short == 'long')
        short_open = (x.state == 'open') & (x.long_short == 'short')
        long_close = (x.state == 'close') & (x.long_short == 'long')
        short_close = (x.state == 'close') & (x.long_short == 'short')
        price = 'price'
        if nums == 1:
            axes.plot(x.index, x[price], c='k')
            axes.plot(x[long_open].index, x[long_open][price], '^', markersize='7', c='r', label='long_open')
            axes.plot(x[long_close].index, x[long_close][price], 'v', markersize='7', c='g', label='long_close')
            axes.plot(x[short_open].index, x[short_open][price], '^', markersize='7', c='b', label='short_open')
            axes.plot(x[short_close].index, x[short_close][price], 'v', markersize='7', c='y', label='short_close')
            axes.set_xlabel(sec, fontsize=13, color='k')
            axes.set_ylabel('Settle Price', fontsize=15, color='k')
            axes.legend(loc='best', fontsize=12)
        else:
            axes[i].plot(x.index, x[price], c='k')
            axes[i].plot(x[long_open].index, x[long_open][price], '^', markersize='7', c='r', label='long_open')
            axes[i].plot(x[long_close].index, x[long_close][price], 'v', markersize='7', c='g', label='long_close')
            axes[i].plot(x[short_open].index, x[short_open][price], '^', markersize='7', c='b', label='short_open')
            axes[i].plot(x[short_close].index, x[short_close][price], 'v', markersize='7', c='y',
                         label='short_close')
            axes[i].set_xlabel(sec, fontsize=13, color='k')
            axes[i].set_ylabel('Settle Price', fontsize=15, color='k')
            axes[i].legend(loc='best', fontsize=12)
    if nums != 1:
        f.subplots_adjust(hspace=0.2)


# 展示买卖信号
def plot_signal(df):
    '''
    Parameters
    ----------
    df:signal series,include signal and close,pandas

    '''
    import pandas as pd
    import numpy as np
    _signal_type = pd.unique(df.signal.dropna())
    if np.in1d(_signal_type, [0, 1, -1]).all():
        df.close.plot(c='k', figsize=(15, 6))
        plt.plot(df[df.signal == 1].index, df[df.signal == 1].close, '^', markersize=6, c='r', label='buy')
        plt.plot(df[df.signal == -1].index, df[df.signal == -1].close, 'v', markersize=6, c='g', label='sell')
        plt.legend(loc='best')
        plt.show()
    else:
        df.close.plot(c='k', figsize=(12, 6.5))
        plt.plot(df[df.signal == 'long open'].index, df[df.signal == 'long open'].close, '^', markersize=6, c='r',
                 label='long open')
        plt.plot(df[df.signal == 'short open'].index, df[df.signal == 'short open'].close, '^', markersize=6, c='b',
                 label='short open')
        plt.plot(df[df.signal == 'long close'].index, df[df.signal == 'long close'].close, 'v', markersize=6, c='g',
                 label='long close')
        plt.plot(df[df.signal == 'short close'].index, df[df.signal == 'short close'].close, 'v', markersize=6, c='y',
                 label='short close')
        plt.legend(loc='best')
        plt.show()


# 展示买卖信号
def plot_signal_minute(df):
    df = df.copy()
    tdx = range(len(df))
    df['pos'] = tdx
    freq = int(len(df) / 20)
    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xticks(tdx[::freq])
    ax.plot(tdx, df.close.values, c='k')
    ax.plot(df[df.signal == 1].pos, df[df.signal == 1].close, "^", markersize=7, c='r', label='buy')
    ax.plot(df[df.signal == -1].pos, df[df.signal == -1].close, "v", markersize=7, c='g', label='sell')
    ax.set_xticklabels([x.to_pydatetime().date() for x in df.index][::freq], rotation=35, horizontalalignment='right',
                       color='k')
    ax.set_xlabel('Date', color='k', size=15)
    ax.set_ylabel('Price', color='k', size=15)
    plt.legend(loc='best')
