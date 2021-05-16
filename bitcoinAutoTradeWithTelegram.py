from datetime import datetime
import time, calendar
import pyupbit
import datetime
import requests
import telegram
import numpy as np

access = "wXFhFCaXWLnkLa9tY5sxQD0OilUDxc7VCTQEvDDe"
secret = "RilFszqAYo6ykeFzgpWM6H8cwx7FK5jos6KoWRai"

token = '1645526009:AAG9k3CZCnkjTNxveXD9Jm4UB728FZkMDYY'    #Api
bot = telegram.Bot(token)
huni_id = 48156792
bot_id = '@HuniCoinBot'

# 매수 할 종목
symbol_list = ['KRW-BTC', 'KRW-XRP', 'KRW-ETH', 'KRW-ADA', 'KRW-DOGE']
bought_list = []
target_buy_count = 5
buy_percent = 0.18
invest_rate = 0

def telegramSend(message):
    """인자로 받은 문자열을 파이썬 셀과 슬랙으로 동시에 출력한다."""
    now = datetime.datetime.now()
    print(now.strftime('[%m/%d %H:%M:%S]'), message)
    
    if now.hour >=6 and now.hour <=23:
        strbuf = datetime.datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
        bot.sendMessage(bot_id, strbuf)

def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    # df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    # target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    # return target_price
 
    df = pyupbit.get_ohlcv(ticker)

    df['noise'] = 1 - abs(df['open'] - df['close']) / (df['high'] - df['low'])
    invest_rate = df['noise'].rolling(20).mean().iloc[-1]
    df['target_price'] = df['close'] + (df['high'] - df['low']) * invest_rate
    target_price = df.iloc[-1]['target_price']
    #telegramSend(str(sym) + ' target price: ' + str(target_price))
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def buy_coin(ticker):
    try:
        global bought_list
        
        if ticker in bought_list:
            return False
        
        target_price = get_target_price(ticker)
        current_price = get_current_price(ticker)
        ma5 = get_ma5(ticker)

        if target_price < current_price and ma5 < current_price:
            krw = get_balance("KRW") * buy_percent
            if krw > 5000000:
                buy_result = upbit.buy_market_order(ticker, krw)
                telegramSend(str(ticker) + ' buy result: ' + str(buy_result))

    except Exception as e:
        print(e)
        telegramSend('buy_coin('+ str(ticker) + ') -> exception! ' + str(e))

def sell_all():
    try:
        for sym in symbol_list:
            coin_balance = get_balance(sym)
            if coin_balance > 0.05:
                sell_result = upbit.sell_market_order(sym, coin_balance)
                telegramSend(str(sym) + "sell : " + str(sell_result))

    except Exception as e:
        print(e)
        telegramSend('sell_coin('+ str(sym) + ') -> exception! ' + str(e))

def send_imformation():
    account_balance = upbit.get_balances()
    print(upbit.get_balances())
    telegramSend("계좌 잔고: " + str(account_balance))

    for sym in symbol_list:
        target_price = get_target_price(sym)
        current_price = get_current_price(sym)
        ma5 = get_ma5(sym)

        if target_price < current_price and ma5 < current_price:
            telegramSend(str(sym) + '은 현재 매수 구간')
        else:
            telegramSend(str(sym) + '은 현재 휴식 구간')        
        
        telegramSend('\n' + str(sym) + ' target price: ' + str(target_price) + '\n'
                        +str(sym) + ' currnet price: ' + str(current_price)+ '\n'
                        +str(sym) + ' 5days MA price: ' + str(ma5))

if __name__ == '__main__': 
    try:

        # 로그인
        upbit = pyupbit.Upbit(access, secret)
        print("autotrade start")
        # 시작 메세지 슬랙 전송
        telegramSend("[HuniCoinBot] autotrade start!!")
        print(upbit.get_balances())

        while True:
            now = datetime.datetime.now()
            start_time = get_start_time("KRW-BTC")
            end_time = start_time + datetime.timedelta(days=1)

            if now.minute == 48 and 0 <= now.second <= 10:
                send_imformation()

            if start_time < now < end_time - datetime.timedelta(seconds=10):
                for sym in symbol_list:
                    if len(bought_list) < target_buy_count:
                        buy_coin(sym)
                        time.sleep(1)
            else:
                sell_all()
                time.sleep(1)

    except Exception as e:
        print(e)
        telegramSend("[HuniCoinBot]", e)
        time.sleep(1)