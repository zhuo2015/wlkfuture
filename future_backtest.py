from .fetch import future_daily, future_minute
from .plot import plot_trades, plot_equity_curve, plot_hold_values, plot_all_new
from .statistic import stats
from .portfolio import *
import datetime
import pandas as pd

# format price data
pd.options.display.float_format = '{:0.4f}'.format


#   策略配置环境
class Context(object):
    def __init__(self):
        self._cash = 1000000  # 起始资金
        self._slippage = 0.246  # 交易滑点
        self._commission = 0.03  # 手续费
        self._start = datetime.datetime(2012, 1, 1)  # 策略起始回测期
        self._minute = None
        self._end = None  # 策略结束回测期
        self._pad = True  # 回测数据前沿(方便技术指标类策略回测)
        self._securities = []  # 订阅标的

    @property
    def cash(self):
        return self._cash

    @cash.setter
    def cash(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('score must be an number')
        self._cash = value

    @property
    def minute(self):
        return self._minute

    @minute.setter
    def minute(self, value):
        if value not in [1, 5, 15, 30, 60]:
            raise TypeError('minute must in [1, 5, 15, 30, 60]')
        self._minute = value

    @property
    def slippage(self):
        return self._slippage

    @slippage.setter
    def slippage(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('score must be an number')
        self._slippage = value

    @property
    def commission(self):
        return self._commission

    @commission.setter
    def commission(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('score must be an number')
        self._commission = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if isinstance(start, (datetime.datetime, datetime.date)):
            self._start = start
        elif isinstance(start, str):
            from dateutil.parser import parse
            start = parse(start)
            self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if isinstance(end, (datetime.datetime, datetime.date)):
            self._end = end
        elif isinstance(end, str):
            from dateutil.parser import parse
            end = parse(end)
            self._end = end

    @property
    def pad(self):
        return self._pad

    @pad.setter
    def pad(self, pad):
        if not isinstance(pad, bool):
            raise TypeError('pad must be bool type')
        self._pad = pad

    @property
    def securities(self):
        return self._securities

    @securities.setter
    def securities(self, securities):
        if not isinstance(securities, list):
            raise TypeError('securities must belong to a list')
        self._securities = securities


# 策略类、包含账户、策略逻辑
class Strategy(object):
    def __init__(self, init, **kwargs):
        self._context = Context()
        #   初始化变量
        init(self._context, **kwargs)

        #   装载策略回测数据
        self._data = self._fetching_data_from_csv(self._context.minute)
        #   初始化账户基本信息
        self._account = Account(self._data, self._context)

    # 从本地读取订阅标的数据（csv文件）
    def _fetching_data_from_csv(self, freq=None):
        delay = 150 if freq is None else 70
        if freq is None:
            pdata = pd.Panel(dict((stk, future_daily(stk)) for stk in self._context.securities))
        else:
            pdata = pd.Panel(dict((stk, future_minute(stk, freq)) for stk in self._context.securities))

        # select trade period
        if self._context.pad:
            pdata = pdata.ix[:, self._context.start - datetime.timedelta(delay):self._context.end, :]
        else:
            pdata = pdata.ix[:, self._context.start:self._context.end, :]
        self._context.end = pdata.major_axis[-1].replace(hour=0, minute=0, second=0)
        self._context.start = pdata.ix[:, self._context.start:, :].major_axis[0].replace(hour=0, minute=0, second=0)
        return pdata

    #   执行回测
    def run_backtest(self, algo, **kwargs):

        # 记录策略耗时
        # import time
        # t0 = time.time()

        # 回测时间戳
        ts_idx = self._data.major_axis  # panel index

        # 按行情序列回测
        for t in ts_idx:
            if t < self._context.start:
                continue

            self._account.now = t
            # 取该时刻及之前数据
            df_ = self._data.ix[:, :t, :]

            # 执行交易逻辑
            algo(df_, self._account, self._context, **kwargs)

            # 每日交易结束后更新净值(日频每日更新，高频每日15点后更新)
            if self._context.minute is None or t.hour == 15:
                # 转换成日频数据的 Timestamp('20XX-XX-XX 00:00:00')
                if self._context.minute is not None:
                    t = t.replace(hour=0, minute=0, second=0)
                self._account._update_account(t)
                # 爆仓了
                if self._account._latest_hold_value(t) < 0:
                    print('you are blasting warehouse', t)
                    break

                    # t1 = time.time()
                    # print('the strategy backtesing consuming %f seconds' % (t1 - t0))

    def get_trading_data(self):
        daily_bal = self._account.daily_bal()
        return self._data, daily_bal

    def get_context(self):
        return self._context

    def backtest_result(self):
        equity_curve = self._account.account_result()
        daily_bal = self._account.daily_bal()
        tlog = self._account.trade_log()
        tpl = self._account.per_trade_pl()
        return equity_curve, daily_bal, tlog, tpl

    def backtest_analysis(self):
        equity_curve = self._account.account_result()
        daily_bal = self._account.daily_bal()
        pl = equity_curve['portfolio']
        _df = pd.DataFrame(stats(daily_bal, pl, self._context.cash))
        return _df.rename(columns={0: 'value'})

    def trade_signal(self):
        daily_bal = self._account.daily_bal()
        plot_trades(daily_bal)

    def equity_curve(self):
        equity_curve = self._account.account_result()
        plot_equity_curve(equity_curve['portfolio'])  # 交易账户类

    def hold_values(self):
        daily_bal = self._account.daily_bal()
        plot_hold_values(daily_bal)

    def plot(self):
        daily_bal = self._account.daily_bal()
        tlog = self._account.trade_log()
        plot_all_new(daily_bal, tlog)


# 账户类（包含回测结果、下单函数、持仓记录，交易记录）
class Account(object):
    def __init__(self, data, context):
        self.now = None  # 当前回测日期
        self._cash = context.cash  # 初始资金
        self._slippage = context.slippage  # 交易滑点
        self._commission = context.commission  # 交易佣金
        self._cash_ts = dict()  # 每日现金余额序列
        self._trade_pl = []  # 每笔平仓盈亏序列
        _da = data.ix[:, context.start:, :]
        self._dbal = DailyBal(_da, context.minute)

    #   返回所有标的的总持仓市值序列
    def _hold_value_series(self):
        daily_panel = self._dbal.get_daily_balance()
        dfs = daily_panel.swapaxes('items', 'minor')
        return dfs['hold_value']

    #   下单能否成交,检查交易方向、金额是否足够，卖出标的量是否足够
    def _valid_order(self, security, price, shares, long_short):
        # 有没平仓的交易时，不能做反向开仓交易
        vol = self.curr_hold(security)

        # 有没平仓的交易时，不能做反向开仓交易
        if vol != 0:
            if self.curr_direction(security) != long_short:
                return 1

        money = abs(price * shares)
        commission = self._commission * 0.01 * money
        # 多开或者空开
        if shares > 0 and (self._cash < money + commission):
            return 2
        # 多平或空平
        elif shares < 0 and vol < abs(shares):
            return 3

    # 检查最新持仓市值,不可调用
    def _latest_hold_value(self, date):
        v_ts = self._hold_value_series()
        v_ts = v_ts.sum(1)
        return v_ts.at[date]

    # 实际成交价
    def _real_price(self, price, direction):
        real = None
        if direction == 'buy':
            real = (1 + self._slippage * 0.01) * price
        elif direction == 'sell':
            real = (1 - self._slippage * 0.01) * price
        return round(real, 2)

    #   更新账户
    def _update_account(self, date):
        self._cash_ts[date] = self._cash
        self._dbal.update_pl(date)

    #   回测结束后调用
    def account_result(self):
        cash_ts = pd.Series(self._cash_ts)
        hold_value_ts = self._hold_value_series().sum(1)
        portfolio_ts = hold_value_ts + cash_ts
        equity_curve = pd.concat([cash_ts, hold_value_ts, portfolio_ts], axis=1)
        equity_curve.columns = ['remaining_cash', 'hold_value', 'portfolio']
        return equity_curve

    #   返回每笔交易盈亏
    def per_trade_pl(self):
        _df = pd.DataFrame(self._trade_pl)
        _df = _df.set_index('close_date')
        return _df

    #   返回交易记录
    def trade_log(self):
        return self._dbal.get_log()

    #   返回持仓市值明细
    def daily_bal(self):
        return self._dbal.get_daily_balance()

    #   可在algo策略中调用，查找标的的最新持仓量
    def curr_hold(self, sec):
        return self._dbal.check_sec_value(sec, 'open_qty')

    #   可在algo策略中调用，查找标的的最新开平方向
    def curr_direction(self, sec):
        return self._dbal.check_sec_value(sec, 'long_short')

    #   可在algo策略中调用，查找策略的最新净值序列
    def curr_portfolio(self):
        v_ts = self._hold_value_series().sum(1)
        c_ts = pd.Series(self._cash_ts)
        p_ts = pd.concat([v_ts, c_ts], axis=1).dropna()
        return p_ts.sum(1)

    #   可在algo策略中调用，查找指定标的前一交易日的持仓市值
    def curr_hold_value(self, sec):
        v_ts = self._hold_value_series()
        holdval = v_ts.ix[:self.now, sec]
        return holdval[:-1]

    # #   可在algo策略中调用，查找当前策略的最大回撤
    # def curr_max_drawdown(self):
    #     return self.latest_n_drawdown(0)

    #   可在algo策略中调用，查找最近n个交易期标的持仓价值的最大回撤
    def latest_n_drawdown(self, sec, n):
        pl = self.curr_hold_value(sec)
        pl = pl[-n:]
        if (pl != 0).all():
            return max(1 - pl / pd.expanding_max(pl))

    # #   可在algo策略中调用，查找最近n个交易期的涨跌幅
    # def latest_n_return(self, n):
    #     pl = self.curr_portfolio()
    #     pl = pl[-n:]
    #     return pl[-1] / pl[0] - 1

    #   可在algo策略中调用，查找持仓的数量
    def hold_nums(self):
        return self._dbal.hold_nums()

    #   现金余额
    @property
    def cash(self):
        return self._cash

    # 按量（手）下单
    def order_shares(self, security, order_price, shares=0, long_short='long', order_check=False, real_price=False):
        '''
            security:标的物
            order_price:下单价格
            shares:数量,正数为开仓,负数为平仓
            long_short:多、空
            order_check:检查订单有效性
            real_price:按滑点更新的真实成交价
        '''
        price = order_price
        if not real_price:
            # 多开或者空平，实际成交价大于下单价
            if (shares > 0 and long_short == 'long') or (shares < 0 and long_short == 'short'):
                price = self._real_price(order_price, 'buy')
            # 多空开或者多平，实际成交价小于下单价
            else:
                price = self._real_price(order_price, 'sell')

        if not order_check:
            _valid = self._valid_order(security, price, shares, long_short)
            if _valid == 1:
                print("wrong direction,thers is another reversed direction order not yet closed", self.now, security)
                return
            elif _valid == 2:
                print("not enough remaining cash", self.now, security)
                return
            elif _valid == 3:
                print("not enough holding volume", self.now, security)
                return

        # 扣除手续费
        self._cash -= self._commission * 0.01 * abs(price * shares)

        if shares > 0:
            #   减去开仓成本
            self._cash -= price * shares
            #   open order update daily balance
            self._dbal.open_update(self.now, security, price, shares, long_short)
        elif shares < 0:
            #   update unclosed order and calculate the 'return cash' and 'close profit loss'
            re_cash, trade_pl = self._dbal.close_update(self.now, security, price, shares, long_short)
            self._cash += re_cash
            trade_pl['close_date'] = self.now
            self._trade_pl.append(trade_pl)

    # 按价值下单
    def order_amount(self, security, price, cash_amount, long_short='long'):
        if (cash_amount > 0 and long_short == 'long') or (cash_amount < 0 and long_short == 'short'):
            price = self._real_price(price, 'buy')
        # 多空开或者多平，实际成交价小于下单价
        else:
            price = self._real_price(price, 'sell')
        shares = int(cash_amount * (1 - self._commission * 0.01) / price)
        self.order_shares(security, price, shares, long_short, order_check=False, real_price=True)

    #   按比例下单(买入则为现金比例，卖出则为组合持仓量比例)
    def order_percent(self, security, price, percent, long_short='long'):
        if percent < -1 or percent > 1:
            print("percent must between - 1 to 1")
            return
        # 多开或者空平，实际成交价大于下单价
        if (percent > 0 and long_short == 'long') or (percent < 0 and long_short == 'short'):
            price = self._real_price(price, 'buy')
        # 空开或者多平，实际成交价小于下单价
        else:
            price = self._real_price(price, 'sell')

        if percent > 0:
            shares = int(self._cash * (1 - self._commission * 0.01) * percent / price)
            self.order_shares(security, price, shares, long_short, order_check=True, real_price=True)
        elif percent < 0:
            vol = self._dbal.check_sec_value(security, 'open_qty')
            shares = int(vol * percent)
            self.order_shares(security, price, shares, long_short, order_check=True, real_price=True)
