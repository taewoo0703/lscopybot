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
        project_dir = os.path.dirname(current_dir)  # core 폴더의 상위 폴더 (프로젝트 루트)
        self.params_dir = os.path.join(project_dir, "params")
        # loop
        self.active = True  # loop active
        # tasks
        self.timer_task = None
        self.emergency_task = None

    async def initialize(self):
        # load all parameters
        logManager.debug(f"params directory: {self.params_dir}")
        _betting_params = self.load_params()
        self.set_betting_params(_betting_params, False)

        # set timer
        self.timer_task = asyncio.create_task(self.timer_update_1s())
        self.timer_task.add_done_callback(self.timer_update_done_callback)

        # start emergency control loop
        self.emergency_task = asyncio.create_task(self.emergency_control_loop())

        # init ExchangeManager
        await exchangeManager.initialize()

    async def on_shutdown(self):
        # save all parameters
        self.save_params()

        # set active false to stop loops
        self.active = False

        # cancel tasks
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
            try:
                await self.timer_task
            except asyncio.CancelledError:
                pass

        if self.emergency_task and not self.emergency_task.done():
            self.emergency_task.cancel()
            try:
                await self.emergency_task
            except asyncio.CancelledError:
                pass

        # shutdown complete
        await logManager.log_message_async("shutdown complete!")


    ##############################
    # Parameter setting
    ##############################
    def set_betting_params(self, _betting_params: BettingParams, save:bool = True):
        global betting_params
        if _betting_params is not None:
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
            await asyncio.sleep(1)
            await self.on_timer_update(time.time(), "1s")

    # on_timer - update
    async def on_timer_update(self, update_timestamp: float, timeframe: str):
        """
        update timer에 의해 호출되는 메서드
        """
        await exchangeManager.on_timer_update()
        logManager.trace(f"on_timer_update - {timeframe} 완료")

    # done call back - update
    def timer_update_done_callback(self, task):
        self.active = False
        try:
            if task.cancelled():
                logManager.log_message("update task was cancelled")
            elif task.exception():
                logManager.log_error_message(task.exception(), "update error")
            else:
                logManager.log_message("update done")
        except Exception as e:
            logManager.log_error_message(e, "update error")


    ##############################
    # User Control
    ##############################
    def set_pause(self, pause: bool) -> None:
        exchangeManager.set_pause(pause)

    def get_status(self) -> dict:
        """
        master, slave1, slave2 연결 여부, 포지션 상태 반환
        """
        result = {
            "connections": {
                "master_connected": exchangeManager.master.connected,
                "slave1_connected": exchangeManager.slave1.connected,
                "slave2_connected": exchangeManager.slave2.connected,
            },
            "positions": {
                "master_positions": exchangeManager.master_positions,
                "slave1_positions": exchangeManager.slave1_positions,
                "slave2_positions": exchangeManager.slave2_positions,
            }
        }
        return result
    
    def get_params(self) -> dict:
        """
        현재 betting params 반환
        """
        result = {
            "betting_params": betting_params
        }
        return result


            
# singleton
core: Core = Core()