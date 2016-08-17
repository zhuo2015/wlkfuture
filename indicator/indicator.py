# encoding = utf-8
import pandas as pd
import talib as ta
import numpy as np
import talib.abstract as taab


#   noly for 1、5 minute high frequency data
def break_exit(data, **kwargs):
    inperiod = kwargs['inperiod']
    outperiod = kwargs['outperiod']
    da = data.copy()
    da['next_open'] = da['open'].shift(-1)
    da['long_break'] = pd.rolling_max(da.high, inperiod).shift(1)
    da['long_exit'] = pd.rolling_min(da.low, outperiod).shift(1)
    da['short_break'] = pd.rolling_min(da.low, inperiod).shift(1)
    da['short_exit'] = pd.rolling_max(da.high, outperiod).shift(1)
    long_in = da.close > da.long_break
    long_exit = da.close < da.long_exit
    short_in = da.close < da.short_break
    short_exit = da.close > da.short_exit
    da['long_signal'] = np.where(long_in, 1, np.where(long_exit, -1, 0))
    da['short_signal'] = np.where(short_in, 1, np.where(short_exit, -1, 0))
    da['ex_price'] = 0
    da.ix[(da.long_signal == 1) | (da.short_signal == -1), 'ex_price'] = da[['sell1', 'next_open']].max(1)
    da.ix[(da.long_signal == -1) | (da.short_signal == 1), 'ex_price'] = da[['buy1', 'next_open']].min(1)
    return da[['open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal', 'ex_price']]


def TURTLE(data, open_in=50, close_out=20):
    df = pd.DataFrame()
    df['close'] = data['close']


def SHADOW(data, upperbound=2, lowerbound=0.01):
    df = pd.DataFrame()
    df['close'] = data['close']
    upper_shadow = data.high - data[['open', 'close']].max(1)
    lower_shadow = data[['open', 'close']].min(1) - data.low
    real_body = abs(data.close - data.open)
    buy = (lower_shadow >= upperbound * real_body) & (upper_shadow <= lowerbound * real_body)
    sell = (upper_shadow >= upperbound * real_body) & (lower_shadow <= lowerbound * real_body)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


def VOLDIFF(data, timeperiod=30):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['swing'] = (data.high - data.low) / data.low
    df['up_std'] = (data.high - data.open) / data.open
    df['dn_std'] = (data.open - data.low) / data.open
    df['std_diff'] = pd.rolling_mean(df.up_std - df.dn_std, timeperiod)
    buy = (df.std_diff.shift(1) < 0) & (df.std_diff > 0)
    sell = (df.std_diff.shift(1) > 0) & (df.std_diff < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df  # [['close', 'signal']]


# MACD
def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
    df = data.join(taab.MACD(data, fastperiod, slowperiod, signalperiod))
    buy = (df.macd.shift(1) < df.macdsignal.shift(1)) & (df.macd > df.macdsignal) & (df.macd > 0) & (df.macdsignal > 0)
    sell = (df.macd.shift(1) > df.macdsignal.shift(1)) & (df.macd < df.macdsignal) & (df.macd < 0) & (df.macdsignal < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# MACD
def MACD2(data, fastperiod=12, slowperiod=26, signalperiod=9):
    df = data.join(taab.MACD(data, fastperiod, slowperiod, signalperiod))
    buy = (df.macd.shift(1) < df.macdsignal.shift(1)) & (df.macd > df.macdsignal)
    sell = (df.macd.shift(1) > df.macdsignal.shift(1)) & (df.macd < df.macdsignal)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   SAR
def SAR(data, acceleration=0.02, maximum=0.2):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['SAR'] = taab.SAR(data, acceleration, maximum)
    buy = (df.SAR.shift(1) > df.close.shift(1)) & (df.SAR < df.close)
    sell = (df.SAR.shift(1) < df.close.shift(1)) & (df.SAR > df.close)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   MIKE
def MIKE(data, timeperiod=21):
    df = pd.DataFrame()
    df['close'] = data['close']
    high = data['high']
    low = data['low']
    typ = (high + low + df.close) / 3
    hlc = (pd.rolling_mean(typ, timeperiod)).shift(1)
    hv = pd.Series(ta.EMA(np.array(pd.rolling_max(high, timeperiod)), 3), index=data.index)
    lv = pd.Series(ta.EMA(np.array(pd.rolling_min(low, timeperiod)), 3), index=data.index)
    stor = pd.Series(ta.EMA(np.array(2 * hv - lv), 3), index=data.index)
    midr = pd.Series(ta.EMA(np.array(hlc + hv - lv), 3), index=data.index)
    wekr = pd.Series(ta.EMA(np.array(hlc * 2 - lv), 3), index=data.index)
    weks = pd.Series(ta.EMA(np.array(hlc * 2 - hv), 3), index=data.index)
    mids = pd.Series(ta.EMA(np.array(hlc - hv + lv), 3), index=data.index)
    stos = pd.Series(ta.EMA(np.array(2 * lv - hv), 3), index=data.index)
    df = pd.concat([df, stor, midr, wekr, weks, mids, stos], axis=1)
    df.columns = ['close', 'stor', 'midr', 'wekr', 'weks', 'mids', 'stos']
    # 建仓逻辑
    buy = (df.close.shift(1) < df.wekr.shift(1)) & (df.close > df.wekr)
    sell = (df.close.shift(1) > df.weks.shift(1)) & (df.close < df.weks)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


def KBAND(data, timeperiod=14):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['ATR'] = taab.ATR(data, timeperiod)
    df['ma'] = pd.rolling_mean(data.close, timeperiod)
    df['upper_kb'] = df.ATR * 2 + df['ma']
    df['lower_kb'] = df['ma'] - df.ATR * 2
    buy = (df.close.shift(1) < df.upper_kb.shift(1)) & (df.close > df.upper_kb)
    sell = (df.close.shift(1) > df.lower_kb.shift(1)) & (df.close < df.lower_kb)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# BOLL
def BOLL(data, timeperiod=25, nbdevup=2, nbdevdn=2, matype=0):
    df = data.join(taab.BBANDS(data, timeperiod, nbdevup, nbdevdn, matype))
    buy = (df.close.shift(1) < df.upperband.shift(1)) & (df.close > df.upperband)
    sell = (df.close.shift(1) > df.lowerband.shift(1)) & (df.close < df.lowerband)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   KDJ
def KDJ(data, fastk_period=13, slowk_period=3, slowd_period=3, slowk_matype=0, slowd_matype=0):
    df = taab.STOCH(data, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period,
                    slowk_matype=slowk_matype, slowd_matype=slowd_matype)
    df.columns = ['K', 'D']
    df['J'] = 3 * df.K - 2 * df.D
    df['close'] = data['close']
    buy = (df.D.shift(1) < 90) & (df.D > 90)
    sell = (df.D.shift(1) > 10) & (df.D < 10)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


def KDJ2(data, fastk_period=3, slowk_period=3, slowd_period=3, slowk_matype=0, slowd_matype=0):
    df = taab.STOCH(data, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period,
                    slowk_matype=slowk_matype, slowd_matype=slowd_matype)
    df.columns = ['K', 'D']
    df['J'] = 3 * df.K - 2 * df.D
    df['close'] = data['close']
    buy = (df.D > 90) & (df.K > 90)
    sell = (df.D < 10) & (df.K < 10)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   ADTM
def ADTM(data, n=23, m=8):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['open_diff'] = data['open'].diff()
    df['high_minus_open'] = data['high'] - data['open']
    df['open_minus_low'] = data['open'] - data['low']
    dtm = np.where(df.open_diff < 0, 0, np.max(df[['open_diff', 'high_minus_open']], 1))
    dbm = np.where(df.open_diff > 0, 0, np.max(df[['open_diff', 'open_minus_low']], 1))
    stm = pd.rolling_sum(dtm, n)
    sbm = pd.rolling_sum(dbm, n)
    df['ADTM'] = np.where(stm > sbm, (stm - sbm) / stm, np.where(stm == sbm, 0, (stm - sbm) / sbm))
    df['MAADTM'] = pd.rolling_mean(df.ADTM, m)
    # 建仓逻辑
    buy_1 = (df.ADTM.shift(1) < df.MAADTM.shift(1)) & (df.ADTM > df.MAADTM)
    buy_2 = (df.ADTM.shift(1) > -0.5) | (df.ADTM < -0.5)
    sell_1 = (df.ADTM.shift(1) > df.MAADTM.shift(1)) & (df.ADTM < df.MAADTM)
    sell_2 = (df.ADTM.shift(1) < 0.5) & (df.ADTM > 0.5)
    buy = buy_1 | buy_2
    sell = sell_1 | sell_2
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   MTM
def MTM(data, timeperiod=6, ma=6):
    df = pd.DataFrame()
    df['MTM'] = data.close.diff(timeperiod)
    df['close'] = data['close']
    df['MAMTM'] = ta.MA(df.MTM.values, ma)
    buy = (df.MTM.shift(1) < df.MAMTM.shift(1)) & (df.MTM > df.MAMTM) & (df.MAMTM > 0)
    sell = (df.MTM.shift(1) > df.MAMTM.shift(1)) & (df.MTM < df.MAMTM) & (df.MAMTM < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   DMI
def DMI(data, timeperiod=14, m=6):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['PDI'] = taab.PLUS_DI(data, timeperiod=timeperiod)
    df['MDI'] = taab.MINUS_DI(data, timeperiod=timeperiod)
    df['ADX'] = pd.rolling_mean(np.abs(df.PDI - df.MDI) / (df.PDI + df.MDI) * 100, m)
    df['ADXR'] = (df.ADX + df.ADX.shift(m)) * 0.5
    buy = (df.PDI.shift(1) < df.MDI.shift(1)) & (df.PDI > df.MDI)
    sell = (df.PDI.shift(1) > df.MDI.shift(1)) & (df.PDI < df.MDI)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# CR 能量指标
def CR(data, timeperiod=26, m1=10, m2=20, m3=40, m4=60):
    mid = ((data['high'] + data['low']) / 2).shift(1)
    temp1 = pd.Series(np.where(data['high'] - mid > 0, data['high'] - mid, 0), index=data.index)
    temp2 = pd.Series(np.where(mid - data['low'] > 0, mid - data['low'], 0), index=data.index)
    cr = pd.rolling_sum(temp1, timeperiod) / pd.rolling_sum(temp2, timeperiod) * 100
    ma1 = (pd.rolling_mean(cr, m1)).shift(1 + m1 / 2.5)
    ma2 = (pd.rolling_mean(cr, m2)).shift(1 + m2 / 2.5)
    ma3 = (pd.rolling_mean(cr, m3)).shift(1 + m3 / 2.5)
    ma4 = (pd.rolling_mean(cr, m4)).shift(1 + m4 / 2.5)
    df = pd.concat([cr, ma1, ma2, ma3, ma4], axis=1)
    df.columns = ['CR', 'MA1', 'MA2', 'MA3', 'MA4']
    df['close'] = data['close']
    # 建仓逻辑
    buy_one = (df.CR.shift(1) < df[['MA1', 'MA2', 'MA3', 'MA4']].shift(1).max(1)) & \
              (df.CR > df[['MA1', 'MA2', 'MA3', 'MA4']].max(1))
    buy_two = (df.CR.shift(1) < 30) & (df.CR > 30)
    buy = buy_one | buy_two
    sell_one = (df.CR.shift(1) > df[['MA1', 'MA2', 'MA3', 'MA4']].shift(1).min(1)) & \
               (df.CR < df[['MA1', 'MA2', 'MA3', 'MA4']].min(1))
    sell_two = (df.CR.shift(1) > 450) & (df.CR < 450)
    sell = sell_one | sell_two
    df['signal'] = np.where(buy_one, 1, np.where(sell_one, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   DMA 平均差指标
def DMA(data, shortPeriod=13, longPeriod=31, signal=10):
    df = pd.DataFrame()
    df['close'] = data['close']
    shortMa = pd.rolling_mean(data['close'], shortPeriod)
    longMa = pd.rolling_mean(data['close'], longPeriod)
    df['DMA'] = shortMa - longMa
    df['AMA'] = pd.rolling_mean(df.DMA, signal)
    # 建仓逻辑
    buy = (df.DMA.shift(1) < df.AMA.shift(1)) & (df.DMA > df.AMA) & (df.DMA > 0) & (df.AMA > 0)
    sell = (df.DMA.shift(1) > df.AMA.shift(1)) & (df.DMA < df.AMA) & (df.DMA < 0) & (df.AMA < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   PPO
def PPO(data, fastperiod=12, slowperiod=26, matype=0):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['PPO'] = taab.PPO(data, fastperiod=fastperiod, slowperiod=slowperiod, matype=matype)
    buy = (df.PPO.shift(1) < 0) & (df.PPO > 0)
    sell = (df.PPO.shift(1) > 0) & (df.PPO < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# #   PPO
# def PVO(data, fastperiod=12, slowperiod=26, signal=9):
#     df = pd.DataFrame()
#     df['close'] = data['close']
#     import talib as ta
#     df['fast_vol'] = ta.EMA(data.volume.values, fastperiod)
#     df['slow_vol'] = ta.EMA(data.volume.values, slowperiod)
#     df['PVO'] = (df.fast_vol - df.slow_vol) / df.slow_vol * 100
#     df['SPVO'] = ta.EMA(df.PVO.values, signal)
#     buy = (df.PVO.shift(1) < df.SPVO.shift(1)) & (df.PVO > df.SPVO) & (df.PVO > 0)
#     sell = (df.PVO.shift(1) > df.SPVO.shift(1)) & (df.PVO < df.SPVO) & (df.PVO < 0)
#     df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
#     df.signal = df.signal.shift(1)
#     return df[['close', 'signal']]


#   VR 成交量变异率
def VR(data, timeperiod=22):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['open'] = data['open']
    df['volume'] = data['volume']
    th = pd.rolling_sum(np.where(df.close > df.open, df.volume, 0), timeperiod)
    tl = pd.rolling_sum(np.where(df.close < df.open, df.volume, 0), timeperiod)
    df['WVR'] = pd.Series(th / tl * 100, index=df.index)
    buy = (df.WVR.shift(1) < 250) & (df.WVR > 250)
    sell = (df.WVR.shift(1) > 70) & (df.WVR < 70)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# OBV 能量潮
def OBV(data, short=5, long=25):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['OBV'] = pd.Series(ta.OBV(np.array(data['close']), np.array(data['volume'])), index=data.index)
    df['SMAOBV'] = pd.rolling_mean(df.OBV, short)
    df['LMAOBV'] = pd.rolling_mean(df.OBV, long)
    # 建仓逻辑
    buy = (df.SMAOBV.shift(1) < df.LMAOBV.shift(1)) & (df.SMAOBV > df.LMAOBV)  # & (df.OBV > 0)
    sell = (df.SMAOBV.shift(1) > df.LMAOBV.shift(1)) & (df.SMAOBV < df.LMAOBV)  # & (df.OBV < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   EMV
def EMV(data, windows=14, m=9):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['volume'] = data['volume']
    df['high'] = data['high']
    df['low'] = data['low']
    vol = pd.rolling_mean(df.volume, windows) / df.volume
    typ = df.high + df.low
    mid = 100 * typ.diff() / typ
    df['EMV'] = pd.rolling_mean(mid * vol * (df.high - df.low) / pd.rolling_mean(df.high - df.low, windows), windows)
    df['MAEMV'] = pd.rolling_mean(df.EMV, m)
    # 建仓逻辑
    buy = (df.EMV.shift(1) < df.MAEMV.shift(1)) & (df.EMV > df.MAEMV) & (df.EMV > 0) & (df.MAEMV > 0)
    sell = (df.EMV.shift(1) > df.MAEMV.shift(1)) & (df.EMV < df.MAEMV) & (df.MAEMV < 0) & (df.EMV < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   EXPMA 指数平均数
def EXPMA(data, fast=15, slow=35):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['EMA_SHORT'] = taab.EMA(data, fast)
    df['EMA_LONG'] = taab.EMA(data, slow)
    # 建仓逻辑
    buy = (df.close.shift(1) < df.EMA_SHORT.shift(1)) & (df.close > df.EMA_SHORT) & (df.EMA_SHORT > df.EMA_LONG)
    sell = (df.close.shift(1) > df.EMA_SHORT.shift(1)) & (df.close < df.EMA_SHORT) & (df.EMA_SHORT < df.EMA_LONG)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# WVAD 威廉变异离散量
def WVAD2(data, timeperiod=12, fast=5, slow=21):
    df = pd.DataFrame()
    df['close'] = data['close']
    a = data['close'] - data['open']
    b = data['high'] - data['low']
    c = (a / b) * data['volume']
    df['WVAD'] = pd.rolling_sum(c, timeperiod)
    df['WVAD_S'] = pd.rolling_mean(df.WVAD, fast)
    df['WVAD_L'] = pd.rolling_mean(df.WVAD, slow)
    # 建仓逻辑
    buy = (df.WVAD_S.shift(1) < df.WVAD_L.shift(1)) & (df.WVAD_S > df.WVAD_L) & (df.WVAD > 0)
    sell = (df.WVAD.shift(1) > df.WVAD_L.shift(1)) & (df.WVAD_S < df.WVAD_L) & (df.WVAD < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# WVAD 威廉变异离散量
def WVAD(data, timeperiod=18, ma=22):
    df = pd.DataFrame()
    df['close'] = data['close']
    a = data['close'] - data['open']
    b = data['high'] - data['low']
    c = (a / b) * data['volume']
    df['WVAD'] = pd.rolling_sum(c, timeperiod)
    df['MAWVAD'] = pd.rolling_mean(df.WVAD, ma)
    # df['WVAD_L'] = pd.rolling_mean(df.WVAD, slow)
    # 建仓逻辑
    buy = (df.WVAD.shift(1) < 0) & (df.WVAD > 0) & (df.MAWVAD > 0)
    sell = (df.WVAD.shift(1) > 0) & (df.WVAD < 0) & (df.MAWVAD < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# BRAR 买卖意愿指标
def BRAR(data, timeperiod=22):
    df = pd.DataFrame()
    df['close'] = data['close']
    upStrong = data['high'] - data['close'].shift(1)
    dnStrong = data['close'].shift(1) - data['low']
    upPush = data['high'] - data['open']
    dnPush = data['open'] - data['low']
    df['BR'] = pd.rolling_sum(upStrong, timeperiod) / pd.rolling_sum(dnStrong, timeperiod) * 100
    df['AR'] = pd.rolling_sum(upPush, timeperiod) / pd.rolling_sum(dnPush, timeperiod) * 100
    # 建仓逻辑
    buy = (df.BR.shift(1) < 120) & (df.BR > 120) & (df.BR > df.AR)  # (rm.czc 加 BR AR条件)
    sell = (df.BR.shift(1) > 60) & (df.BR < 60) & (df.BR < df.AR)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# TRIX 三重指数平滑移动平均
def TRIX(data, timeperiod=12, signalperiod=7):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['TRIX'] = ta.TRIX(np.array(df.close), timeperiod) * 100
    df['MATRIX'] = pd.rolling_mean(df.TRIX, signalperiod)
    # 建仓逻辑
    buy = (df.TRIX.shift(1) < df.MATRIX.shift(1)) & (df.TRIX > df.MATRIX)
    sell = (df.TRIX.shift(1) > df.MATRIX.shift(1)) & (df.TRIX < df.MATRIX)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# CCI 顺势指标
def CCI(data, timeperiod=16):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['CCI'] = taab.CCI(data, timeperiod=timeperiod)
    # 建仓逻辑
    buy = (df.CCI.shift(1) < 120) & (df.CCI > 120)
    sell = (df.CCI.shift(1) > -100) & (df.CCI < -100)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# ROC 变动率指标
def ROC(data, timeperiod=12, signalperiod=6):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['ROC'] = ta.ROCP(np.array(df.close), timeperiod)
    df['MAROC'] = pd.rolling_mean(df.ROC, signalperiod)
    # 建仓逻辑
    buy = ((df.ROC.shift(1) < df.MAROC.shift(1)) & (df.ROC > df.MAROC)) & (df.ROC < 6.5)
    sell = ((df.ROC.shift(1) > df.MAROC.shift(1)) & (df.ROC < df.MAROC)) & (df.ROC > -6.5)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# WR 威廉指标
def WR(data, timeperiod=14):
    df = pd.DataFrame()
    df['close'] = data['close']
    high = np.array(data['high'])
    close = np.array(data['close'])
    low = np.array(data['low'])
    df['WR'] = pd.Series(ta.WILLR(high, low, close, timeperiod), index=data.index)
    # 建仓逻辑
    buy = (df.WR.shift(1) < -50) & (df.WR > -50) & ((df.WR.shift(3) < -80) | (df.WR.shift(4) < -80))
    sell = (df.WR.shift(1) > -50) & (df.WR < -50) & ((df.WR.shift(3) > -20) | (df.WR.shift(4) > -20))
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# RSI 相对强弱指标 done
def RSI(data, shortperiod=6, longperiod=24, oversold=30, overbought=70):
    df = pd.DataFrame()
    df['close'] = data['close']
    close = np.array(df.close)
    df['RSI_SHORT'] = ta.RSI(close, shortperiod)
    df['RSI_LONG'] = ta.RSI(close, longperiod)
    # 建仓逻辑
    buy = (df.RSI_SHORT.shift(1) < df.RSI_LONG.shift(1)) & (
        df.RSI_SHORT > df.RSI_LONG) & (df.RSI_SHORT.shift(1) < overbought)
    sell = (df.RSI_SHORT.shift(1) > df.RSI_LONG.shift(1)) & (
        df.RSI_SHORT < df.RSI_LONG) & (df.RSI_SHORT.shift(1) > oversold)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# RSI 相对强弱指标 done
def RSI2(data, shortperiod=20, longperiod=55, oversold=20, overbought=80):
    df = pd.DataFrame()
    df['close'] = data['close']
    close = np.array(df.close)
    df['RSI_SHORT'] = ta.RSI(close, shortperiod)
    df['RSI_LONG'] = ta.RSI(close, longperiod)
    # 建仓逻辑
    buy = (df.RSI_SHORT.shift(1) < df.RSI_LONG.shift(1)) & (
        df.RSI_SHORT > df.RSI_LONG) & (df.RSI_SHORT.shift(1) < overbought) & (df.RSI_SHORT > 55)
    sell = (df.RSI_SHORT.shift(1) > df.RSI_LONG.shift(1)) & (
        df.RSI_SHORT < df.RSI_LONG) & (df.RSI_SHORT.shift(1) > oversold) & (df.RSI_SHORT < 55)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   BIAS 乖离率
def BIAS(data, m1=6, m2=12, m3=24):
    df = pd.DataFrame()
    df['close'] = data['close']
    close = data['close']
    bias1 = (close - pd.rolling_mean(close, m1)) / pd.rolling_mean(close, m1) * 100
    bias2 = (close - pd.rolling_mean(close, m2)) / pd.rolling_mean(close, m2) * 100
    bias3 = (close - pd.rolling_mean(close, m3)) / pd.rolling_mean(close, m3) * 100
    df = pd.concat([close, bias1, bias2, bias3], axis=1)
    df.columns = ['close', 'BIAS_S', 'BIAS_M', 'BIAS_L']
    # 建仓逻辑
    buy = (df.BIAS_L.shift(1) < np.max(df[['BIAS_M', 'BIAS_S']].shift(1), 1)) & (
        df.BIAS_L > np.max(df[['BIAS_M', 'BIAS_S']], 1))
    sell = (df.BIAS_L.shift(1) > np.max(df[['BIAS_M', 'BIAS_S']].shift(1), 1)) & (
        df.BIAS_L < np.max(df[['BIAS_M', 'BIAS_S']], 1))
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# PSY 心理线指标
def PSY(data, n=12, m=6, **kwargs):
    df = pd.DataFrame()
    df['close'] = data['close']
    up = pd.Series(np.where(df.close.diff() > 0, 1, 0), index=data.index)
    df['PSY'] = pd.rolling_sum(up, n) / n * 100
    df['MAPSY'] = pd.rolling_mean(df.PSY, m)
    # 建仓逻辑
    buy_one = (df.PSY.shift(1) > 10) & (df.PSY < 10)
    sell_one = (df.PSY.shift(1) < 90) & (df.PSY > 90)
    buy_two = (df.PSY.shift(1) < df.MAPSY.shift(1)) & (df.PSY > df.MAPSY)
    sell_two = (df.PSY.shift(1) > df.MAPSY.shift(1)) & (df.PSY < df.MAPSY)
    buy = buy_one | buy_two
    sell = sell_one | sell_two
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# OSC 变动速率线
def OSC(data, n=20, m=6):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['OSC'] = (df.close - pd.rolling_mean(df.close, n)) * 100
    df['MAOSC'] = pd.Series(ta.EMA(np.array(df.OSC), m), index=df.index)
    # 建仓逻辑
    buy = (df.OSC.shift(1) < df.MAOSC.shift(1)) & (df.OSC > df.MAOSC)
    sell = (df.OSC.shift(1) > df.MAOSC.shift(1)) & (df.OSC < df.MAOSC)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   MFI 资金流量指标
def MFI(data, timeperiod=14):
    df = pd.DataFrame()
    df['close'] = data['close']
    high = np.array(data['high'])
    low = np.array(data['low'])
    close = np.array(data['close'])
    volume = np.array(data['volume'])
    df['MFI'] = pd.Series(ta.MFI(high, low, close, volume, timeperiod), index=data.index)
    # 建仓逻辑
    buy = (df.MFI.shift(1) > 10) & (df.MFI < 0)
    sell = (df.MFI.shift(1) < 90) & (df.MFI > 90)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#   CE 吊灯止损 Chandelier Exit
def CHANDLR(data, n=22, longPosition=3, shortPosition=3):
    df = pd.DataFrame()
    df['close'] = data['close']
    df['ATR'] = ta.ATR(np.array(data['high']), np.array(data['low']), np.array(data['close']), n)
    df['CE_LONG'] = pd.rolling_max(data['high'], n) - df.ATR * longPosition
    df['CE_SHORT'] = pd.rolling_min(data['low'], n) + df.ATR * shortPosition
    # 建仓逻辑
    buy = (df.close.shift(1) < df.CE_SHORT.shift(1)) & (df.close > df.CE_SHORT)
    sell = (df.close.shift(1) > df.CE_SHORT.shift(1)) & (df.close < df.CE_SHORT)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#  AROON阿隆优化指标
def AROON(data, periods=20):
    df = pd.DataFrame()
    df['close'] = data['close']
    high = np.array(data['high'])
    low = np.array(data['low'])
    aroondown, aroonup = ta.AROON(high, low, periods)
    df['AROON_DOWN'] = pd.Series(aroondown, index=data.index)
    df['AROON_UP'] = pd.Series(aroonup, index=data.index)
    df['AROON'] = df.AROON_UP - df.AROON_DOWN
    # 建仓逻辑
    buy_one = (df.AROON_UP.shift(1) < 70) & (df.AROON_UP > 70) & df.AROON > 0
    sell_one = (df.AROON_DOWN.shift(1) < 70) & (df.AROON_DOWN < 70) & df.AROON < 0
    buy_two = (df.AROON_DOWN.shift(1) > 50) & (df.AROON_DOWN < 50) & df.AROON > 0
    sell_two = (df.AROON_UP.shift(1) > 50) & (df.AROON_UP < 50) & df.AROON < 0
    buy = buy_one | buy_two
    sell = sell_one | sell_two
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


#  chaikinAD 离散指标(A/D)
def CHAIKIN(data, fastperiod=9, slowperiod=13):
    df = pd.DataFrame()
    df['close'] = data['close']
    high = np.array(data['high'])
    low = np.array(data['low'])
    close = np.array(data['close'])
    volume = np.array(data['volume'])
    df['CHAIKIN'] = pd.Series(ta.ADOSC(high, low, close, volume, fastperiod, slowperiod), index=data.index)
    # 建仓逻辑
    buy = (df.CHAIKIN.shift(1) < 0) & (df.CHAIKIN > 0)
    sell = (df.CHAIKIN.shift(1) > 0) & (df.CHAIKIN < 0)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]


# 钱德动量摆动
def CMO(data, timeperiod=14):
    df = pd.DataFrame()
    close = np.array(data['close'])
    df['close'] = close
    df['CMO'] = pd.Series(ta.CMO(close, timeperiod), index=data.index)
    # 建仓逻辑
    buy = (df.CMO.shift(1) < 50) & (df.CMO > 50)
    sell = (df.CMO.shift(1) > -50) & (df.CMO < -50)
    df['signal'] = np.where(buy, 1, np.where(sell, -1, np.nan))
    df.signal = df.signal.shift(1)
    return df[['close', 'signal']]
