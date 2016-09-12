from datetime import datetime, timedelta

END_DAY = str((datetime.today() - timedelta(1)).date())
MINUTE_COL_1 = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'position']
MINUTE_COL_2 = ['date', 'open', 'high', 'low', 'close', 'buy1', 'sell1', 'volume', 'amt', 'position']
DAILY_COL = ['date', 'open', 'high', 'low', 'close', 'settle', 'volume', 'amount', 'position']

FUTURE_DAILY_DATA_LOCATION = "D:/Data/Futures/Daily/"

FUTURE_MINUTE_DATA_LOCATION = "D:/Data/Futures/Minute/"

# 上期货
_SHF = ['cu', 'al', 'zn', 'pb', 'au', 'ag', 'rb',
        'ru', 'fu', 'wr', 'bu', 'hc', 'ni', 'sn']

# 大商所
_DCE = ['a', 'm', 'y', 'p', 'c', 'i', 'jm', 'j',
        'l', 'v', 'b', 'jd', 'fb', 'bb', 'pp', 'cs']

# 郑商所
_CZC = ['wh', 'oi', 'cf', 'sr', 'ri', 'zc', 'ta', 'fg',
        'ma', 'rm', 'rs', 'pm', 'jr', 'lr', 'sm', 'sf']
# 所有期货合约代码
SECS = sum([_SHF, _DCE, _CZC], [])

_MON = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
_YEAR = ['10', '11', '12', '13', '14', '15', '16', '17']
_DATES = [y + x for y in _YEAR for x in _MON]
CODES = [name + date for name in SECS for date in _DATES]

# 主连代码
_SHFZL = {'cu': 'ZL000003', 'al': 'ZL000001', 'zn': 'ZL000006', 'pb': 'ZL000025', 'au': 'ZL000002', 'ag': 'ZL000028',
          'rb': 'ZL000023', 'ru': 'ZL000005', 'fu': 'ZL000004', 'wr': 'ZL000022', 'bu': 'ZL000033', 'hc': 'ZL000040',
          'ni': 'ZL000046', 'sn': 'ZL000047'}

_CZCZL = {'wh': 'ZL000012', 'oi': 'ZL000009', 'cf': 'ZL000007', 'sr': 'ZL000010', 'ri': 'ZL000021', 'zc': 'ZL000035',
          'ta': 'ZL000011', 'fg': 'ZL000029', 'ma': 'ZL000027', 'rm': 'ZL000031', 'rs': 'ZL000030', 'pm': 'ZL000013',
          'jr': 'ZL000038', 'lr': 'ZL000042',
          'sm': 'ZL000044', 'sf': 'ZL000043'}

_DCEZL = {'a': 'ZL000014', 'm': 'ZL000018', 'y': 'ZL000020', 'p': 'ZL000019', 'c': 'ZL000016', 'i': 'ZL000034',
          'jm': 'ZL000032', 'j': 'ZL000026', 'l': 'ZL000017', 'v': 'ZL000024', 'b': 'ZL000015', 'jd': 'ZL000039',
          'fb': 'ZL000036', 'bb': 'ZL000037', 'pp': 'ZL000041', 'cs': 'ZL000045'}

MAIN_CONTRACT = dict()
MAIN_CONTRACT.update(_SHFZL)
MAIN_CONTRACT.update(_CZCZL)
MAIN_CONTRACT.update(_DCEZL)

# 主力合约换月数据字段
FU_NAME_2 = {b'\xb5\xf7\xd5\xfb\xc8\xd5\xc6\xda': 'date', b'\xd6\xf7\xc1\xa6\xb4\xfa\xc2\xeb': 'code',
             b'\xd6\xf7\xc1\xa6\xd4\xc2\xb7\xdd': 'month'}
