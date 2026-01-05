from core.LogManager import logManager
from core.schemas import BettingParams
from typing import Literal
import asyncio, ebest, copy
from settings import settings
from datetime import datetime
from core.types import *
from core.ExchangeManager import *


# Master API 로그인
exchangeManager.initialize()
api: ebest.OpenApi = exchangeManager.master # 테스트용 API 객체

# ------------- 해외선물 미결제잔고내역 조회 -------------
inputs = {
    'CIDBQ01500InBlock1': {
        'AcntTpCode': AcntTpCode.GENERAL, # 계좌구분코드
        'QryDt': '', # 조회일자
        'BalTpCode': BalTpCode.COMBINED, # 잔고구분코드
    },
}
response = await api.request('CIDBQ01500', inputs)  # type: ignore
if not response['status']:
    logManager.error(f"해외선물 미결제잔고내역 조회 실패: {api.last_message}")
results = response.body['CIDBQ01500OutBlock2']
"""
results 예시:
[{
    'IsuCodeVal':'ADM23',       # 종목코드
    'CrcyCodeVal':'USD',        # 통화코드
    'OvrsDrvtPrdtCode':'AD',    # 해외파생상품코드
    'OvrsDrvtOptTpCode':'F',    # 해외파생옵션구분코드
    'BnsTpCode':'1',            # 매매구분코드
    'CmnCodeNm':'매도',         # 공통코드
    'TpCodeNm':'일반',          # 구분코드
    'BalQty':2,                 # 잔고수량
    'PchsPrc':'0.6713',         # 매입단가
}, ... ]
"""



# ------------- 해외선물 신규주문 -------------
# 사전 설정값
IsuCodeVal = 'MNQH23'
bnsTpCode = BnsTpCode.LONG  # 매수
abrdFutsOrdPtnCode = AbrdFutsOrdPtnCode.MARKET  # 시장가
OvrsDrvtOrdPrc = 0  # 해외파생주문가격 (시장가 주문 시 0)
CndiOrdPrc = 0  # 조건주문가격 (조건주문 미사용 시 0)
OrdQty = 1  # 주문수량

inputs = {
    'CIDBT00100InBlock1': {
        'OrdDt': '', # 주문일자
        'IsuCodeVal': IsuCodeVal, # 종목코드값
        'FutsOrdTpCode': FutsOrdTpCode.NEW, # 선물주문구분코드
        'BnsTpCode': bnsTpCode, # 매매구분코드
        'AbrdFutsOrdPtnCode': AbrdFutsOrdPtnCode, # 해외선물주문유형코드
        'CrcyCode': SPACE, # 통화코드
        'OvrsDrvtOrdPrc': OvrsDrvtOrdPrc, # 해외파생주문가격
        'CndiOrdPrc': CndiOrdPrc, # 조건주문가격
        'OrdQty': OrdQty, # 주문수량
        'PrdtCode': SPACE, # 상품코드
        'DueYymm': SPACE, # 만기년월
        'ExchCode': SPACE, # 거래소코드
    },
}
response = await api.request('CIDBT00100', inputs) # type: ignore
if not response: 
    logManager.error(f"해외선물 신규주문 실패: {api.last_message}")

results = response.body['CIDBT00100OutBlock2']
ovrsFutsOrgOrdNo = results['OvrsFutsOrdNo']
"""
results 예시:
{
    'AcntNo':'20629783903',        # 계좌번호
    'OvrsFutsOrdNo':'0000000136',  # 해외선물주문번호
}
"""



# ------------- 해외선물 취소주문 -------------
# 사전 설정값
IsuCodeVal = IsuCodeVal # 종목코드값
OvrsFutsOrgOrdNo = ovrsFutsOrgOrdNo  # 해외선물원주문번호

inputs = {
    'CIDBT01000InBlock1': {
        'OrdDt': '', # 주문일자
        'IsuCodeVal': IsuCodeVal, # 종목코드값
        'OvrsFutsOrgOrdNo': OvrsFutsOrgOrdNo, # 해외선물원주문번호
        'FutsOrdTpCode': FutsOrdTpCode.CANCEL, # 선물주문구분코드
        'PrdtTpCode': SPACE, # 상품구분코드
        'ExchCode': SPACE, # 거래소코드
    },
}
response = await api.request('CIDBT01000', inputs)  # type: ignore
if not response: 
    logManager.error(f"해외선물 취소주문 실패: {api.last_message}")

results = response.body['CIDBT01000OutBlock2']