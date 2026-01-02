from settings import settings
from .LogManager import logManager
import asyncio

class EmergencyControl:
    def __init__(self):
        self.coroutine_queue = []

    async def update(self):
        if self.coroutine_queue:
            for coroutine in self.coroutine_queue:
                try:
                    logManager.debug(f"[EmergencyControl-update] coroutine start : {coroutine}")
                    await coroutine
                except Exception as e:
                    logManager.log_error_message(f"[EmergencyControl-update] {e}")
            self.coroutine_queue.clear()

    ##################################################  Append Task Queue  ##################################################
    # def remove_symbols_force(self, exchange_name: EXCHANGE_LITERAL, symbols: list[str]) -> None:
    #     from protocol import SymbolsRequest
    #     from main import remove_symbols_force
    #     request = SymbolsRequest(
    #         password=settings.PASSWORD,
    #         exchange_name=exchange_name,
    #         symbols=symbols
    #     )

    #     self.coroutine_queue.append(remove_symbols_force(request))
    #     logManager.info(f"[EmergencyControl-AddTask] remove_symbols_force: {exchange_name} {symbols}")

    # def remove_all_symbols_force(self, exchange_name: EXCHANGE_LITERAL) -> None:
    #     from protocol import ExchangeRequest
    #     from main import remove_all_symbols_force
    #     request = ExchangeRequest(
    #         password=settings.PASSWORD,
    #         exchange_name=exchange_name
    #     )

    #     self.coroutine_queue.append(remove_all_symbols_force(request)) 
    #     logManager.info(f"[EmergencyControl-AddTask] remove_all_symbols_force: {exchange_name}")



# singleton
emergencyControl: EmergencyControl = EmergencyControl()