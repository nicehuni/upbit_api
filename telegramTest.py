#pip install python-telegram-bot
#pip install telepot

from datetime import datetime
import time, calendar
import telegram

token = '1645526009:AAG9k3CZCnkjTNxveXD9Jm4UB728FZkMDYY'    #Api
bot = telegram.Bot(token)
huni_id = 48156792
bot_id = '@HuniCoinBot'

def telegramSend(message):
    """인자로 받은 문자열을 파이썬 셸과 슬랙으로 동시에 출력한다."""
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    bot.sendMessage(bot_id, strbuf)

telegramSend('안녕하세요. Huni가 운영하는 Coin 투자 알림 Bot입니다.')

