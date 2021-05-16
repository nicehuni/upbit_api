import pyupbit

# 로그인
access = "wXFhFCaXWLnkLa9tY5sxQD0OilUDxc7VCTQEvDDe"          # 본인 값으로 변경
secret = "RilFszqAYo6ykeFzgpWM6H8cwx7FK5jos6KoWRai"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

# 잔고 조회
print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회