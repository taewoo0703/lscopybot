from .LogManager import logManager
from .schemas import *
import asyncio, os, pickle, time
from datetime import datetime, timedelta
from settings import settings
from .EmergencyControl import emergencyControl
from .ExchangeManager import exchangeManager


class Core:
    def __init__(self):
        self.emergency_control = emergencyControl
        # save/load
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.params_dir = os.path.join(current_dir, "params")
        # loop
        self.active = True  # loop active

    async def initialize(self):
        # load all parameters
        logManager.debug(f"params directory: {self.params_dir}")
        _betting_params = self.load_params()
        self.set_betting_params(_betting_params, False)

        # set timer
        timer_update_1s_task = asyncio.create_task(self.timer_update_1s())
        timer_update_1s_task.add_done_callback(self.timer_update_done_callback)

        # start emergency control loop
        emergency_control_task = asyncio.create_task(self.emergency_control_loop())

        # init ExchangeManager
        await exchangeManager.initialize()

    async def on_shutdown(self):
        # save all parameters
        self.save_params()

        # shutdown complete
        logManager.log_message("shutdown complete!")


    ##############################
    # Parameter setting
    ##############################
    def set_betting_params(self, _betting_params: BettingParams, save:bool = True):
        betting_params = _betting_params
        if save:
            self.save_betting_params()


    ##############################
    # Save/Load parameters
    ##############################
    def save_betting_params(self):
        if not os.path.exists(self.params_dir):
            os.makedirs(self.params_dir)
        
        with open(os.path.join(self.params_dir, "betting_params.pkl"), "wb") as f:
            pickle.dump(betting_params, f)

    def save_params(self):
        self.save_betting_params()

    def check_file(self, parent_dir: str, file_name: str) -> bool:
        file_path = os.path.join(parent_dir, file_name)
        if not os.path.exists(parent_dir):
            return False
        if not os.path.isfile(file_path):
            return False
        return True

    def load_betting_params(self):
        if self.check_file(self.params_dir, "betting_params.pkl"):
            with open(os.path.join(self.params_dir, "betting_params.pkl"), "rb") as f:
                return pickle.load(f)
        else:
            return None

    def load_params(self):
        _betting_params= self.load_betting_params()
        return _betting_params


    ##############################
    # Emergency Control loop
    ##############################
    async def emergency_control_loop(self):
        while self.active:
            await self.emergency_control.update()
            await asyncio.sleep(1)


    ##############################
    # Timer event
    ##############################
    # timer - update
    async def timer_update_1s(self):
        """
        매 1초마다 on_timer_update 메서드 호출
        """
        while self.active:
            now = datetime.now()
            next_minute = (now.minute // 1 + 1) * 1
            if next_minute == 60:
                next_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            else:
                next_time = now.replace(minute=next_minute, second=0, microsecond=0)
            wait_time = (next_time - now).total_seconds()
            logManager.debug(f"update_1s - {next_time}까지 대기: {wait_time}초")
            await asyncio.sleep(wait_time)
            await self.on_timer_update(next_time.timestamp(), "1s")

    # on_timer - update
    async def on_timer_update(self, update_timestamp: float, timeframe: str):
        """
        update timer에 의해 호출되는 메서드
        """
        pass

    # done call back - update
    def timer_update_done_callback(self, task):
        self.active = False
        try:
            if task.exception():
                logManager.log_error_message(task.exception(), "update error")
            else:
                logManager.log_message("update done")
        except Exception as e:
            logManager.log_error_message(e, "update error")





            
# singleton
core: Core = Core()