from enum import Enum

SPACE = ' '

class AcntTpCode(str, Enum):
    """
    계좌구분코드
    """
    GENERAL = '1'   # 위탁계좌
    ISA = '2'       # 중개계좌


class BalTpCode(str, Enum):
    """
    잔고구분코드
    """
    COMBINED = '1' # 합산
    SEPARATE = '2' # 건별

class BnsTpCode(str, Enum):
    """
    매매구분코드
    """
    ALL = '0'     # 전체
    SHORT = '1'   # 매도
    LONG = '2'    # 매수

class AbrdFutsOrdPtnCode(str, Enum):
    """
    해외선물주문유형코드
    """
    MARKET = '1'      # 시장가
    LIMIT = '2'       # 지정가

class FutsOrdTpCode(str, Enum):
    """
    선물주문구분코드
    """
    NEW = '1'        # 신규
    CHANGE = '2'     # 정정
    CANCEL = '3'     # 취소