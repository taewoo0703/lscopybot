from dataclasses import dataclass
from typing import Literal


@dataclass
class BettingParams:
    slave1_multiple: int = 1
    slave2_multiple: int = 1

betting_params: BettingParams = BettingParams()