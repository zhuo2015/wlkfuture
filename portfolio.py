import pandas as pd

_FUTURE_COLUMNS = ['date', 'price', 'hold_volume', 'state', 'long_short', 'cost', 'hold_value']

_UNCLOSED_ORDER_COLUMNS = ['price', 'open_qty', 'long_short']
_TRADE_LOG_COLUMNS = ['trade_date', 'security', 'price', 'qty', 'direction', 'long_short']


class TradeState:
    OPEN = 'open'
    CLOSE = 'close'
    HOLD = 'hold'


# 各标的每日持仓及持仓市值、交易记录
class DailyBal(object):
    """ Log for daily balance """

    def __init__(self, data, freq):
        # pandas.panel of daily balance of every security
        self._tlog = pd.DataFrame(columns=_TRADE_LOG_COLUMNS)
        self._start = data.major_axis[0]
        self._pdata = self._init_daily_bal(data, freq)
        self._unclosed = self._init_unclosed_order(data.items)

    @staticmethod
    def _init_daily_bal(data, freq):
        _dd = dict()
        for sec in data.items:
            _df = pd.DataFrame(columns=_FUTURE_COLUMNS)
            _df['date'] = data.major_axis
            _df['hold_volume'] = 0
            _df['state'] = TradeState.HOLD
            _df['cost'] = 0
            _df['hold_value'] = 0
            df = data[sec]
            _df['price'] = df.settle.fillna(method='ffill').values if freq is None else df.close.fillna(
                method='ffill').values
            _df['long_short'] = None
            _df = _df.set_index('date')
            _dd[sec] = _df
        return pd.Panel(_dd)

    @staticmethod
    def _init_unclosed_order(secs):
        res = dict()
        for sec in secs:
            _df = pd.DataFrame(columns=_UNCLOSED_ORDER_COLUMNS)
            res[sec] = _df
        return res

    #   记录下单
    def record_trade(self, order_date, security, price, qty, direction, long_short):
        _t = {'price': price, 'qty': abs(qty), 'long_short': long_short, 'trade_date': order_date, 'security': security,
              'direction': direction}
        self._tlog = self._tlog.append(_t, ignore_index=True)
        if direction == 'open':
            _df = self._unclosed[security]
            _df = _df.append({'price': price, 'open_qty': qty, 'long_short': long_short}, ignore_index=True)
            self._unclosed[security] = _df
        elif direction == 'close':
            return self.cal_cost_cash(security, price, -qty)

    # 返回交易记录表
    def get_log(self):
        """ return Dataframe """
        return self._tlog.set_index('trade_date')

    # 计算新的持仓成本、及返回的现金数量
    def cal_cost_cash(self, security, close_price, closed_qty):
        _df = self._unclosed[security]
        re_cash_cost = 0  # 返回的成本
        re_cash_pl = 0  # 返回的盈亏
        pre_cost = (_df.price * _df.open_qty).sum()  # 以前的总成本
        new_vol = _df['open_qty'].sum() - closed_qty  # 新的持仓量
        assert new_vol >= 0  # 新的持仓量
        for i in _df.index:
            vol = _df.at[i, 'open_qty']
            price = _df.at[i, 'price']
            l_s = _df.at[i, 'long_short']
            if vol < closed_qty:
                re_cash_pl += vol * (close_price - price) if l_s == 'long' else vol * (price - close_price)
                re_cash_cost += vol * price
                _df.at[i, 'open_qty'] = 0
                closed_qty -= vol
            elif vol >= closed_qty:
                re_cash_pl += closed_qty * (close_price - price) if l_s == 'long' else closed_qty * (
                    price - close_price)
                re_cash_cost += closed_qty * price
                _df.at[i, 'open_qty'] = vol - closed_qty
                break
        # print(new_vol)
        _df = _df[_df.open_qty != 0]
        _df.index = range(len(_df))
        self._unclosed[security] = _df
        re_cash = re_cash_pl + re_cash_cost  # 返回的总现金
        new_cost = pre_cost - re_cash_cost
        _dd = {'cost': re_cash_cost, 'returns': re_cash_pl / re_cash_cost, 'trade_pl': re_cash_pl, 'trade_type': l_s}
        return re_cash, new_cost, new_vol, _dd

    #   返回所有标的每日持仓信息
    def get_daily_balance(self):
        return self._pdata

    def hold_nums(self):
        res = 0
        for i, x in self._unclosed.items():
            if len(x) != 0:
                res += 1
        return res

    # 查询指定标的，指定内容（item:交易成本、多空状态、持仓量）,指定日期前一期的值
    def previous_sec_value(self, date, sec, item):
        df = self._pdata[sec]
        if date != self._start:
            return df.loc[:date, item].iat[-2]
        else:
            return df.at[date, item]

    # 查询指定标的，指定内容（item:交易成本、多空状态、持仓量）,指定日期前一期的值
    def previous_sec_value2(self, date, sec, item):
        df = self._unclosed[sec]
        if item == 'hold_volume':
            return df['open_qty'].sum()

    # 开单更新：原始持仓量、成本加上新的开仓量及开仓成本
    def open_update(self, date, sec, price, shares, long_short):

        #   record trade
        self.record_trade(date, sec, price, shares, 'open', long_short)

        open_order = self._unclosed[sec]
        df = self._pdata[sec]
        df.at[date, 'hold_volume'] = open_order['open_qty'].sum()
        df.at[date, 'cost'] = (open_order.open_qty * open_order.price).sum()
        df.at[date, 'state'] = TradeState.OPEN
        df.at[date, 'long_short'] = long_short

    def close_update(self, date, sec, price, shares, long_short):

        return_cash, cost, vol, trade_pl = self.record_trade(date, sec, price, shares, 'close', long_short)

        df = self._pdata[sec]
        df.at[date, 'hold_volume'] = vol
        df.at[date, 'cost'] = cost
        df.at[date, 'state'] = TradeState.CLOSE
        df.at[date, 'long_short'] = long_short
        return return_cash, trade_pl

    # 根据每日结算价变化更新账户每日盈亏
    def update_pl(self, date):
        if self._start == date:
            return
        for sec in self._pdata.items:
            df = self._pdata[sec]
            if df.at[date, 'state'] == TradeState.HOLD:
                df.at[date, 'hold_volume'] = df.loc[:date, 'hold_volume'].iat[-2]
                if df.at[date, 'hold_volume'] != 0:
                    df.at[date, 'cost'] = df.loc[:date, 'cost'].iat[-2]
                    df.at[date, 'long_short'] = df.loc[:date, 'long_short'].iat[-2]
            cal_value = df['price'] * df['hold_volume']
            short_value = 2 * df['cost'] - cal_value
            df.loc[df.long_short == 'long', 'hold_value'] = cal_value[df.long_short == 'long']
            df.loc[df.long_short == 'short', 'hold_value'] = short_value[df.long_short == 'short']
