from utility.BaseLogManager import BaseLogManager, log_level_under
from settings import settings
from typing import Literal
from dhooks import Embed
from .types import *

class LogManager(BaseLogManager):
    def __init__(self, discord_webhook_url: str | None = None):
        super().__init__(discord_webhook_url)


    # 포지션 변경 메세지
    @log_level_under("INFO")
    async def log_position_change_message_async(self, positions: list[dict]):
        """
        positions =
            [
                {
                    'code': 'MNQH23',  # 종목코드
                    'qty': 2,          # 수량
                    'direction': BnsTpCode.LONG,  # 매매구분코드
                },
                ...
            ]
        """
        description_lines = []
        for pos in positions:
            direction = "LONG" if pos['direction'] == BnsTpCode.LONG else "SHORT"
            description_lines.append(f"[{pos['code']}] {direction} / Qty : {pos['qty']}")
        description = "\n".join(description_lines)

        embed = Embed(
            title=f"[포지션 변경 알림]",
            description=description,
            color=0x00FF00,
        )
        await self.log_message_async(embed=embed)



    # 신규 주문 메세지
    @log_level_under("DEBUG")
    async def log_order_message_async(self, order_info: dict, type: APIType):
        """
        order_info =
            {
                'OrdDt': self.get_today(), # 주문일자
                'IsuCodeVal': IsuCodeVal, # 종목코드값
                'FutsOrdTpCode': FutsOrdTpCode.NEW, # 선물주문구분코드
                'BnsTpCode': _BnsTpCode, # 매매구분코드
                'AbrdFutsOrdPtnCode': _AbrdFutsOrdPtnCode, # 해외선물주문유형코드
                'CrcyCode': SPACE, # 통화코드
                'OvrsDrvtOrdPrc': OvrsDrvtOrdPrc, # 해외파생주문가격
                'CndiOrdPrc': CndiOrdPrc, # 조건주문가격
                'OrdQty': OrdQty, # 주문수량
                'PrdtCode': SPACE, # 상품코드
                'DueYymm': SPACE, # 만기년월
                'ExchCode': SPACE, # 거래소코드
            }
        """
        direction = "LONG" if order_info['BnsTpCode'] == BnsTpCode.LONG else "SHORT"
        embed = Embed(
            title=f"[{type}] 신규 주문",
            description=f"[{order_info['IsuCodeVal']}] {direction} / Qty : {order_info['OrdQty']}",
            color=0x0000FF,
        )
        await self.log_message_async(embed=embed)

    # 취소 주문 메세지
    @log_level_under("DEBUG")
    async def log_cancel_order_message_async(self, order_info: dict, type: APIType):
        """
        order_info =
            {
                'OrdDt': self.get_today(), # 주문일자
                'IsuCodeVal': IsuCodeVal, # 종목코드값
                'OvrsFutsOrgOrdNo': OvrsFutsOrgOrdNo, # 해외선물원주문번호
                'FutsOrdTpCode': FutsOrdTpCode.CANCEL, # 선물주문구분코드
                'PrdtTpCode': SPACE, # 상품구분코드
                'ExchCode': SPACE, # 거래소코드
            }
        """
        embed = Embed(
            title=f"[{type}] 취소 주문",
            description=f"[{order_info['IsuCodeVal']}] Order No. : {order_info['OvrsFutsOrgOrdNo']}",
            color=0xFFFFFF,
        )
        await self.log_message_async(embed=embed)

    # -------------------------------------------- ERROR MESSAGES --------------------------------------------
    # 신규 주문 에러 메세지
    @log_level_under("ERROR")
    async def log_order_error_message_async(self, error: str | Exception, order_info: dict, type: APIType):
        """
        order_info =
            {
                'OrdDt': self.get_today(), # 주문일자
                'IsuCodeVal': IsuCodeVal, # 종목코드값
                'FutsOrdTpCode': FutsOrdTpCode.NEW, # 선물주문구분코드
                'BnsTpCode': _BnsTpCode, # 매매구분코드
                'AbrdFutsOrdPtnCode': _AbrdFutsOrdPtnCode, # 해외선물주문유형코드
                'CrcyCode': SPACE, # 통화코드
                'OvrsDrvtOrdPrc': OvrsDrvtOrdPrc, # 해외파생주문가격
                'CndiOrdPrc': CndiOrdPrc, # 조건주문가격
                'OrdQty': OrdQty, # 주문수량
                'PrdtCode': SPACE, # 상품코드
                'DueYymm': SPACE, # 만기년월
                'ExchCode': SPACE, # 거래소코드
            }
        """
        if isinstance(error, Exception):
            error = self.get_error(error)

        embed = Embed(
            title=f"[{type}] 신규 주문 실패",
            description=f"[{order_info['IsuCodeVal']}] Qty : {order_info['OrdQty']}\nError: {error}",
            color=0xFF0000,
        )
        await self.log_message_async(embed=embed)

    # 취소 주문 에러 메세지
    @log_level_under("ERROR")
    async def log_cancel_order_error_message_async(self, error: str | Exception, order_info: dict, type: APIType):
        """
        order_info =
            {
                'OrdDt': self.get_today(), # 주문일자
                'IsuCodeVal': IsuCodeVal, # 종목코드값
                'OvrsFutsOrgOrdNo': OvrsFutsOrgOrdNo, # 해외선물원주문번호
                'FutsOrdTpCode': FutsOrdTpCode.CANCEL, # 선물주문구분코드
                'PrdtTpCode': SPACE, # 상품구분코드
                'ExchCode': SPACE, # 거래소코드
            }
        """
        if isinstance(error, Exception):
            error = self.get_error(error)

        embed = Embed(
            title=f"[{type}] 취소 주문 실패",
            description=f"[{order_info['IsuCodeVal']}] Order No. : {order_info['OvrsFutsOrgOrdNo']}\nError: {error}",
            color=0xFF0000,
        )
        await self.log_message_async(embed=embed)

    # 포지션 조회 에러 메세지
    @log_level_under("ERROR")
    async def log_fetch_positions_error_message_async(self, error: str | Exception, type: APIType):
        if isinstance(error, Exception):
            error = self.get_error(error)

        embed = Embed(
            title=f"[{type}] 포지션 조회 실패",
            description=f"Error: {error}",
            color=0xFF0000,
        )
        await self.log_message_async(embed=embed)


# singleton
logManager = LogManager(settings.DISCORD_WEBHOOK_URL)
