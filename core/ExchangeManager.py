from .LogManager import logManager
from .schemas import *
from typing import Literal
import asyncio, ebest, copy
from settings import settings
from datetime import datetime
from .types import *

class ExchangeManager:
    def __init__(self):
        # exchange API instances
        self.master: ebest.OpenApi = ebest.OpenApi()
        self.slave1: ebest.OpenApi = ebest.OpenApi()
        self.slave2: ebest.OpenApi = ebest.OpenApi()

        # connected status
        self.master_connected: bool = False
        self.slave1_connected: bool = False
        self.slave2_connected: bool = False
        
        # positions
        self.master_positions = []  # [{'code': 종목코드, 'qty': 잔고수량, 'direction': BnsTpCode}, ...]
        self.slave1_positions = []
        self.slave2_positions = []

        # prev positions
        self.prev_master_positions = []
        self.prev_slave1_positions = []
        self.prev_slave2_positions = []

        # flags
        self.login_dirty = False
        self.pause = False
        self.double_check = False
        self.double_check_counter = 0
        self.double_check_max = 3

    async def initialize(self) -> None:
        # login
        await self.login(self.master)
        await self.login(self.slave1)
        await self.login(self.slave2)

        # set connected status
        self.master_connected = self.master._connected
        self.slave1_connected = self.slave1._connected
        self.slave2_connected = self.slave2._connected

    def get_today(self) -> str:
        return datetime.now().strftime('%Y%m%d')

    # 로그인
    async def login(self, api: ebest.OpenApi) -> bool:
        app_key = ""
        secret_key = ""
        name = ""
        if api == self.master:
            app_key = settings.MASTER_APP_KEY
            secret_key = settings.MASTER_SECRET_KEY
            name = "master"
        elif api == self.slave1:
            app_key = settings.SLAVE1_APP_KEY
            secret_key = settings.SLAVE1_SECRET_KEY
            name = "slave1"
        elif api == self.slave2:
            app_key = settings.SLAVE2_APP_KEY
            secret_key = settings.SLAVE2_SECRET_KEY
            name = "slave2"
        else:
            await logManager.log_error_message_async("Unknown API instance", "Login Error")
            return False
        
        if not await api.login(app_key, secret_key):
            await logManager.log_error_message_async(f"[{name}] {api._last_message}", "API Login Error")
            return False
        
        await logManager.log_message_async(f"[{name}] Login successful")
        return True

    # 해외선물 미결제잔고내역 조회
    async def fetch_open_positions(self, api: ebest.OpenApi, type: APIType) -> None | list[dict]:
        """
        해외선물 미결제잔고내역 조회
        returns: list(dict)
        예) [{
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
        inputs = {
            'CIDBQ01500InBlock1': {
                'AcntTpCode': AcntTpCode.GENERAL, # 계좌구분코드
                'QryDt': '', # 조회일자
                'BalTpCode': BalTpCode.COMBINED, # 잔고구분코드
            },
        }
        response = await api.request('CIDBQ01500', inputs)
        if not response: 
            await logManager.log_fetch_positions_error_message_async(f'API Request Error({api.last_message})', type)
            self.check_rsp_msg(api.last_message)
            return None
        if 'CIDBQ01500OutBlock2' in response.body:
            return response.body['CIDBQ01500OutBlock2']
        else:
            await logManager.log_fetch_positions_error_message_async(response.response_text, type)
            self.check_rsp_msg(response.response_text)
            return None

    # 해외선물 신규주문
    async def request_new_order(self, 
                                api: ebest.OpenApi, 
                                IsuCodeVal: str, # 종목코드
                                _BnsTpCode: BnsTpCode, # 매매구분코드
                                _AbrdFutsOrdPtnCode: AbrdFutsOrdPtnCode, # 해외선물주문유형코드
                                OvrsDrvtOrdPrc: float, # 해외파생주문가격
                                CndiOrdPrc: float, # 조건주문가격
                                OrdQty: int, # 주문수량
                                type: APIType,
                            ) -> None | dict:
        """
        해외선물 신규주문
        returns: dict
        예) {
                'AcntNo':'20629783903',        # 계좌번호
                'OvrsFutsOrdNo':'0000000136',  # 해외선물주문번호
            }
        """
        inputs = {
            'CIDBT00100InBlock1': {
                'OrdDt': '', # 주문일자
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
            },
        }
        response = await api.request('CIDBT00100', inputs)
        if not response: 
            await logManager.log_order_error_message_async(f'API Request Error({api.last_message})', inputs['CIDBT00100InBlock1'], type)
            self.check_rsp_msg(api.last_message)
            return None
        if 'CIDBT00100OutBlock2' in response.body:
            await logManager.log_order_message_async(inputs['CIDBT00100InBlock1'], type)
            return response.body['CIDBT00100OutBlock2']
        else:
            await logManager.log_order_error_message_async(response.response_text, inputs['CIDBT00100InBlock1'], type)
            self.check_rsp_msg(response.response_text)
            return None

    # 해외선물 취소주문
    async def request_cancel_order(self, 
                                   api: ebest.OpenApi,
                                    IsuCodeVal: str, # 종목코드
                                    OvrsFutsOrgOrdNo: str, # 해외선물원주문번호
                                ) -> None | dict:
        """
        해외선물 취소주문
        returns: dict
        예) {
                'AcntNo':'20629783903',        # 계좌번호
                'OvrsFutsOrdNo':'0000000136',  # 해외선물주문번호
            }
        """
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
        response = await api.request('CIDBT01000', inputs)
        if not response: 
            await logManager.log_cancel_order_error_message_async(f'API Request Error({api.last_message})', inputs['CIDBT01000InBlock1'], type)
            self.check_rsp_msg(api.last_message)
            return None
        if 'CIDBT01000OutBlock2' in response.body:
            await logManager.log_cancel_order_message_async(inputs['CIDBT01000InBlock1'], type)
            return response.body['CIDBT01000OutBlock2']
        else:
            await logManager.log_cancel_order_error_message_async(response.response_text, inputs['CIDBT01000InBlock1'], type)
            self.check_rsp_msg(response.response_text)
            return None

    # 포지션 업데이트
    async def update_positions(self) -> None:
        # master positions
        if self.master_connected:
            master_positions = await self.fetch_open_positions(self.master, APIType.MASTER)
            if master_positions is not None:
                self.master_positions = [{'code': pos['IsuCodeVal'], 'qty': int(pos['BalQty']), 'direction': pos['BnsTpCode']} for pos in master_positions]

        # slave1 positions
        if self.slave1_connected:
            slave1_positions = await self.fetch_open_positions(self.slave1, APIType.SLAVE1)
            if slave1_positions is not None:
                self.slave1_positions = [{'code': pos['IsuCodeVal'], 'qty': int(pos['BalQty']), 'direction': pos['BnsTpCode']} for pos in slave1_positions]

        # slave2 positions
        if self.slave2_connected:
            slave2_positions = await self.fetch_open_positions(self.slave2, APIType.SLAVE2)
            if slave2_positions is not None:
                self.slave2_positions = [{'code': pos['IsuCodeVal'], 'qty': int(pos['BalQty']), 'direction': pos['BnsTpCode']} for pos in slave2_positions]

    # 포지션 카피
    async def copy_positions(self):
        """
        master에 있는 포지션을 slave1, slave2에 카피
        """
        if self.slave1_connected:
            await self.copy_positions_to_slave(self.slave1, self.slave1_positions, APIType.SLAVE1)
        if self.slave2_connected:
            await self.copy_positions_to_slave(self.slave2, self.slave2_positions, APIType.SLAVE2)

    async def copy_positions_to_slave(self, slave_api: ebest.OpenApi, slave_positions: list[dict], type: APIType):
        """
        master_positions와 slave_positions를 비교해서 차이만큼 주문
        """
        if not slave_api._connected:
            await logManager.log_error_message_async("Slave API not connected", "Connection Error")
            return

        # 모든 종목 코드 수집
        all_codes = set()
        for pos in self.master_positions:
            all_codes.add(pos['code'])
        for pos in slave_positions:
            all_codes.add(pos['code'])

        # 종목별로 차이 계산 및 주문
        for code in all_codes:
            # master의 net position 계산 (LONG: +, SHORT: -)
            master_net = 0
            for pos in self.master_positions:
                if pos['code'] == code:
                    if pos['direction'] == BnsTpCode.LONG:
                        master_net += pos['qty']
                    elif pos['direction'] == BnsTpCode.SHORT:
                        master_net -= pos['qty']

            # slave의 net position 계산 (LONG: +, SHORT: -)
            slave_net = 0
            for pos in slave_positions:
                if pos['code'] == code:
                    if pos['direction'] == BnsTpCode.LONG:
                        slave_net += pos['qty']
                    elif pos['direction'] == BnsTpCode.SHORT:
                        slave_net -= pos['qty']

            # 필요한 주문량과 방향 계산
            multiple = 1
            if (type == APIType.SLAVE1):
                multiple = betting_params.slave1_multiple
            elif (type == APIType.SLAVE2):
                multiple = betting_params.slave2_multiple
            diff = master_net * multiple - slave_net
            
            if diff == 0:
                continue  # 차이가 없으면 주문할 필요 없음
                
            order_qty = abs(diff)
            order_direction = BnsTpCode.LONG if diff > 0 else BnsTpCode.SHORT
            
            try:
                result = await self.request_new_order(
                    api=slave_api,
                    IsuCodeVal=code,
                    _BnsTpCode=order_direction,
                    _AbrdFutsOrdPtnCode=AbrdFutsOrdPtnCode.MARKET,
                    OvrsDrvtOrdPrc=0,  # 시장가이므로 0
                    CndiOrdPrc=0,
                    OrdQty=order_qty,
                    type=type
                )
                
                # if not result:
                #     self.login_dirty = True
                    
            except Exception as e:
                await logManager.log_error_message_async(f"[{type.value}]Error ordering {code}: {str(e)}", "Order Error")
        
    # 포지션 두개 비교
    def compare_positions(self, a: list[dict], b: list[dict]) -> bool:
        """
        두 포지션 리스트가 동일한지 비교
        포지션 리스트 type : [{'code': 종목코드, 'qty': 잔고수량, 'direction': BnsTpCode}, ...]
        
        returns: True if equal, False if not
        """
        if len(a) != len(b):
            return False
        a_sorted = sorted(a, key=lambda x: x['code'])
        b_sorted = sorted(b, key=lambda x: x['code'])
        return a_sorted == b_sorted
    
    # 타이머 업데이트
    async def on_timer_update(self) -> None:
        """
        모든 계좌의 포지션 업데이트
        master가 달라진게 있는지 체크
        master에 변화가 있으면 slave1, slave2에 카피
        """
        if self.pause:
            return

        # check login dirty
        if self.login_dirty:
            await logManager.log_debug_message_async("Re-login due to login dirty...")
            await self.relogin()
            self.login_dirty = False

        # update positions
        await self.update_positions()
        
        # compare master positions
        if not self.compare_positions(self.master_positions, self.prev_master_positions):
            await logManager.log_position_change_message_async(self.master_positions)
            # log_message_async("Master positions changed, copying to slaves...")
            await self.copy_positions()
            self.double_check = True
            self.double_check_counter = 0

        # double check
        if self.double_check:
            self.double_check_counter += 1
            if self.double_check_counter >= self.double_check_max:
                # copy positions again
                await logManager.log_debug_message_async("Double check: copying positions again...")
                await self.copy_positions()
                self.double_check = False
                self.double_check_counter = 0
                

        # save prev positions
        self.prev_master_positions = copy.deepcopy(self.master_positions)
        self.prev_slave1_positions = copy.deepcopy(self.slave1_positions)
        self.prev_slave2_positions = copy.deepcopy(self.slave2_positions)

    # set pause
    def set_pause(self, pause: bool) -> None:
        self.pause = pause
    
    # check response message
    def check_rsp_msg(self, rsp_msg: str):
        if ErrorMsg.EXPIRED_TOKEN in rsp_msg:
            self.login_dirty = True
        elif ErrorMsg.INVALID_TOKEN in rsp_msg:
            self.login_dirty = True
        elif ErrorMsg.SERVICE_DELAY in rsp_msg:
            return
        elif ErrorMsg.NOT_ENOUGH_BALANCE in rsp_msg:
            return

    # relogin
    async def relogin(self) -> None:
        # login
        if self.master_connected:
            await self.master.close()
            await self.login(self.master)
        if self.slave1_connected:
            await self.slave1.close()
            await self.login(self.slave1)
        if self.slave2_connected:
            await self.slave2.close()
            await self.login(self.slave2)

        # set connected status
        self.master_connected = self.master._connected
        self.slave1_connected = self.slave1._connected
        self.slave2_connected = self.slave2._connected

# singleton instance
exchangeManager = ExchangeManager()
