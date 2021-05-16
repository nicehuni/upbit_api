import pyupbit
import numpy as np
import pandas as pd

df = pyupbit.get_ohlcv("KRW-BTC", count=7, to="20210419")
df = df.drop(['value'], axis=1)

# 변동성 돌파 기준 범위 계산, (고가-저가) * k값
df['range'] = (df['high'] - df['low']) * 0.5

# range 컬럼을 한칸씩 밑으로 내려서 해당 행 시가와 더해 매수타켓 가격을 구함
df['target'] = df['open'] + df['range'].shift(1)

# ror(rate of return: 수익율), np.where(조건문, 참일 때 값, 거짓 때 값)
fee = 0.05
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'] - fee,
                     1)

# 누적 곱 계산(cumprod) => 누적 수익율
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산((누적 최대 hpr - 현재 hpr) / 누적 최대 hpr * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
print(df)
print("MDD(%): ", df['dd'].max())

df.to_excel("dd.xlsx")