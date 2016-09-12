import pandas as pd

_DAILY_BALANCE_COLUMNS = ['date', 'price', 'hold_volume', 'long_short', 'cost', 'hold_value']

_UNCLOSED_ORDER_COLUMNS = ['price', 'open_qty', 'long_short', 'cost']
_TRADE_LOG_COLUMNS = ['date', 'security', 'price', 'qty', 'direction', 'long_short']


class TradeState:
    OPEN = 'open'
    CLOSE = 'close'
    HOLD = 'hold'


# 各标的每日持仓及持仓市值、交易记录
class DailyBal(object):
    """ Log for daily balance """

    def __init__(self, data, freq):
        # pandas.dataframe of every trading record
        self._tlog = pd.DataFrame(columns=_TRADE_LOG_COLUMNS)
        # pandas.panel of daily balance of every security
        self._pdata = self._init_daily_bal(data, freq)
        # dict of every security's unclosed order
        self._unclosed = self._init_unclosed_order(data.items)

    @staticmethod
    def _init_daily_bal(data, freq):
        _dd = dict()
        if freq is not None:
                tdx = pd.unique([x.replace(hour=0, minute=0, second=0) for x in data.major_axis])
        else:
            tdx = data.major_axis
        for sec in data.items:
            _df = pd.DataFrame(columns=_DAILY_BALANCE_COLUMNS)
            _df['date'] = tdx
            _df['hold_volume'] = 0
            _df['cost'] = 0
            _df['hold_value'] = 0
            _df['price'] = data[sec].settle.fillna(method='ffill').values if freq is None \
                else data[sec].at_time('15:00').close.fillna(method='ffill').values
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
        _t = {'price': price, 'qty': abs(qty), 'long_short': long_short, 'date': order_date, 'security': security,
              'direction': direction}

        self._tlog = self._tlog.append(_t, ignore_index=True)

        if direction == 'open':
            _df = self._unclosed[security]
            t = {'price': price, 'open_qty': qty, 'long_short': long_short, 'cost': qty * price}
            _df = _df.append(t, ignore_index=True)
            self._unclosed[security] = _df
        elif direction == 'close':
            return self.cal_cost_cash(security, price, -qty)

    # 返回交易记录表
    def get_log(self):
        """ return Dataframe """
        return self._tlog.set_index('date')

    # 计算新的持仓成本、及返回的现金数量
    def cal_cost_cash(self, security, close_price, closed_qty):
        _df = self._unclosed[security]
        re_cash_cost = 0  # 返回的成本
        re_cash_pl = 0  # 返回的盈亏
        new_vol = _df['open_qty'].sum() - closed_qty  # 新的持仓量
        assert new_vol >= 0  # 新的持仓量
        for i in _df.index:
            vol_i = _df.at[i, 'open_qty']
            price_i = _df.at[i, 'price']
            l_s = _df.at[i, 'long_short']
            price_diff = close_price - price_i
            if vol_i < closed_qty:
                re_cash_pl += vol_i * price_diff if l_s == 'long' else vol_i * price_diff * (-1)
                re_cash_cost += vol_i * price_i
                _df.at[i, 'open_qty'] = 0
                _df.at[i, 'cost'] = 0
                closed_qty -= vol_i
            elif vol_i >= closed_qty:
                re_cash_pl += closed_qty * price_diff if l_s == 'long' else closed_qty * price_diff * (-1)
                re_cash_cost += closed_qty * price_i
                _df.at[i, 'open_qty'] = vol_i - closed_qty
                _df.at[i, 'cost'] = _df.at[i, 'open_qty'] * price_i
                break

        _df = _df[_df.open_qty != 0]
        _df.index = range(len(_df))
        self._unclosed[security] = _df
        re_cash = re_cash_pl + re_cash_cost  # 返回的总现金
        _dd = {'cost': re_cash_cost, 'returns': re_cash_pl / re_cash_cost, 'trade_pl': re_cash_pl, 'trade_type': l_s}
        return re_cash, _dd

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
    def check_sec_value(self, sec, item):
        df = self._unclosed[sec]
        if item == 'open_qty':
            return df[item].sum()
        elif item == 'long_short':
            return df[item].values[-1]

    # 开单更新：原始持仓量、成本加上新的开仓量及开仓成本
    def open_update(self, date, sec, price, shares, long_short):

        #   record trade
        self.record_trade(date, sec, price, shares, 'open', long_short)

    def close_update(self, date, sec, price, shares, long_short):

        return_cash, trade_pl = self.record_trade(date, sec, price, shares, 'close', long_short)
        return return_cash, trade_pl

    # 更新账户每日持仓量、持仓成本及持仓市值(依据每日收盘价/结算价)
    def update_pl(self, date):

        for sec in self._pdata.items:
            df = self._pdata[sec]
            open_order = self._unclosed[sec]
            if len(open_order) != 0:
                hold_volume = open_order['open_qty'].sum()
                cost = open_order['cost'].sum()
                ls = open_order['long_short'].iat[-1]
                df.at[date, 'hold_volume'] = hold_volume
                df.at[date, 'cost'] = cost
                df.at[date, 'long_short'] = ls
                cal_value = df.at[date, 'price'] * hold_volume
                df.at[date, 'hold_value'] = cal_value if ls == 'long' else 2 * cost - cal_value
