from .LogManager import logManager
from .schemas import BettingParams
from typing import Literal
import asyncio
import ebest
from settings import settings

class ExchangeManager:
    def __init__(self):
        # exchange API instances
        self.master: ebest.OpenApi = ebest.OpenApi()
        self.slave1: ebest.OpenApi = ebest.OpenApi()
        self.slave2: ebest.OpenApi = ebest.OpenApi()
        
        # positions
        self.master_positions = {}  # {symbol: quantity}
        self.slave1_positions = {}
        self.slave2_positions = {}

        

    async def initialize(self) -> None:
        # login - master
        if not await self.master.login(settings.MASTER_APP_KEY, settings.MASTER_SECRET_KEY):
            await logManager.log_error_message_async(f"[master] {self.master._last_message}", "API Login Error")
        
        # login - slave1
        if not await self.slave1.login(settings.SLAVE1_APP_KEY, settings.SLAVE1_SECRET_KEY):
            await logManager.log_error_message_async(f"[slave1] {self.slave1._last_message}", "API Login Error")
        
        # login - slave2
        if not await self.slave2.login(settings.SLAVE2_APP_KEY, settings.SLAVE2_SECRET_KEY):
            await logManager.log_error_message_async(f"[slave2] {self.slave2._last_message}", "API Login Error")
        
    async def clone_positions(self):
        pass

    async def 
    
# singleton instance
exchangeManager = ExchangeManager()
