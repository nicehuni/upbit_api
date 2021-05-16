import pyupbit
import pybithumb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

fee = 0
k = 0.5
investManageRule = 2

df = pyupbit.get_ohlcv("KRW-BTC") #, to='20210430', count=90)
df = df.drop(['value'], axis=1)
print(df.tail())
#df = pybithumb.get_ohlcv("BTC")

df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
df['bull'] = df['open'] > df['ma5']

df['range'] = (df['high'] - df['low']) * k
df['target'] = df['open'] + df['range'].shift(1)

df['volatility'] = df['range'] / df['close'] * 100

df['invest'] = np.where(df['volatility'] > investManageRule,
                        investManageRule / df['volatility'],
                        1)

# 1.������ ���� ������ ����
df['ror1'] = np.where(df['high'] > df['target'], 
                     df['close'] / df['target'] - fee,
                     1)
df['hpr1'] = df['ror1'].cumprod()
df['dd1'] = (df['hpr1'].cummax() - df['hpr1']) / df['hpr1'].cummax() * 100

# 2.������ ���� ���� + �����? ����
df['ror2'] = np.where((df['high'] > df['target']) & df['bull'], 
                     df['close'] / df['target'] - fee,
                     1)
df['hpr2'] = df['ror2'].cumprod()
df['dd2'] = (df['hpr2'].cummax() - df['hpr2']) / df['hpr2'].cummax() * 100

# 3.������ ���� ���� + ���� ������ ���� ���� ���� ����
df['ror3'] = np.where(df['high'] > df['target'],
                      df['close'] / df['target'] * (1-fee/100) * df['invest'] + (1 - df['invest']),
                      1)
df['hpr3'] = df['ror3'].cumprod()
df['dd3'] = (df['hpr3'].cummax() - df['hpr3']) / df['hpr3'].cummax() * 100

# 4.������ ���� ���� + �����? + ���� ������ ���� ���� ���� ����
df['ror4'] = np.where((df['high'] > df['target']) & df['bull'],
                     df['close'] / df['target'] * (1-fee/100) * df['invest'] + (1 - df['invest']),
                     1)
df['hpr4'] = df['ror4'].cumprod()
df['dd4'] = (df['hpr4'].cummax() - df['hpr4']) / df['hpr4'].cummax() * 100

# 5.������ ���� ���� + �����? + noise ���� 
# �Ϻ��� ������ ���? noise = 1 - abs(open-close)/(high-low)
df['noise'] = 1-abs(df['open']-df['close'])/(df['high']-df['low'])
df['noise_ma20'] = df['noise'].rolling(window=20, min_periods=1).mean().shift(1)
df['noise_target'] = df['open'] + df['range'].shift(1) * df['noise_ma20']

df['ror5'] = np.where((df['high'] > df['noise_target']) & df['bull'], 
                     df['close'] / df['noise_target'] - fee,
                     1)
df['hpr5'] = df['ror5'].cumprod()
df['dd5'] = (df['hpr5'].cummax() - df['hpr5']) / df['hpr5'].cummax() * 100

# 6.������ ���� ���� + noise ���� + ���� ������ ���� ���� ���� ����
df['ror6'] = np.where(df['high'] > df['noise_target'], 
                      df['close'] / df['noise_target'] * (1-fee/100) * df['invest'] + (1 - df['invest']),
                      1)
df['hpr6'] = df['ror6'].cumprod()
df['dd6'] = (df['hpr6'].cummax() - df['hpr6']) / df['hpr6'].cummax() * 100

# print
print("RoR(%): ", df['hpr1'][-2], df['hpr2'][-2], df['hpr3'][-2], df['hpr4'][-2], df['hpr5'][-2], df['hpr6'][-2] )
print("MDD(%): ", df['dd1'].max(), df['dd2'].max(), df['dd3'].max(), df['dd4'].max(), df['dd5'].max(), df['dd6'].max())

#plt.rc('font', family='Malgun Gothic')
plt.figure(figsize=(10,5))
plt.ylabel('Rate of Return')
#plt.plot(df['close'])
plt.plot(df['hpr1'], 'r', label='NoRule')
plt.plot(df['hpr2'], 'b', label='Bull')
plt.plot(df['hpr3'], 'g', label='BitRate')
plt.plot(df['hpr4'], 'm', label='Bull+BitRate')
plt.plot(df['hpr5'], 'r--', label='Bull+Noise')
plt.plot(df['hpr6'], 'y', label='Noise+BitRate')
plt.grid(True)
plt.legend()
plt.show()
