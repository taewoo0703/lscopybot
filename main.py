from fastapi.exception_handlers import request_validation_exception_handler
from fastapi import FastAPI, Request, status, BackgroundTasks, Query
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import traceback, ipaddress, asyncio, os, json, httpx
from contextlib import asynccontextmanager

from settings import settings
from protocol import *
from core import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logManager.initialize()
    await core.initialize()
    await logManager.log_message_async(f"LS Copy Bot 실행 완료! - 버전: {VERSION}")
    
    yield
    
    # Shutdown
    try:
        await core.on_shutdown()
    except Exception as e:
        logManager.log_error_message(f"Shutdown error: {e}", "Shutdown Error")


# global instance
VERSION = "LS Copy Bot ver 1.0"
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

##############################
# routing
##############################
@app.get("/")
async def get_home():
    return RedirectResponse(url="/static/home.html")

@app.get("/admin")
async def get_admin():
    return RedirectResponse(url="/static/admin.html")

##############################
# fundamental functinos
##############################

whitelist = [
    "127.0.0.1",
]
whitelist = whitelist + settings.WHITELIST


@app.middleware("http")
async def whitelist_middleware(request: Request, call_next):
    try:
        if (settings.USE_WHITELIST and request.client.host not in whitelist and not ipaddress.ip_address(request.client.host).is_private):
            msg = f"{request.client.host}는 안됩니다"
            print(msg)
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=f"{request.client.host}는 허용되지 않습니다",
            )
    except:
        logManager.log_error_message(traceback.format_exc(), "미들웨어 에러")
    else:
        response = await call_next(request)
        return response
    
    
@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    msgs = [
        f"[에러{index+1}] " + f"{error.get('msg')} \n{error.get('loc')}"
        for index, error in enumerate(exc.errors())
    ]
    message = "[Error]\n"
    for msg in msgs:
        message = message + msg + "\n"

    logManager.log_error_message(f"{message}\n {exc.body}", "validation_exception_handler")
    return await request_validation_exception_handler(request, exc)


##########################################
# parameter setting
##########################################
@app.post("/set_betting_params")
async def set_betting_params(request: BettingParamsRequest):
    """ betting params 설정 """
    core.set_betting_params(request.betting_params)
    return f"betting params 설정 완료"


##########################################
# monitoring
##########################################
@app.post("/view_status")
async def view_status(request: BaseRequest):
    result = core.get_status()
    return result

@app.post("/view_params")
async def view_params(request: BaseRequest):
    result = core.get_params()
    return result


##########################################
# utility
##########################################
@app.get("/use_whitelist/{use}")
async def use_whitelist(use: str):
    use_bool = use.lower() in ("true", "1", "yes", "on")
    settings.USE_WHITELIST = use_bool
    return f"use_whitelist: {use_bool}"


##########################################
# external interrupt
##########################################
@app.post("/pause")
async def pause(request: BaseRequest):
    core.set_pause(True)
    return f"Paused"

@app.post("/resume")
async def resume(request: BaseRequest):
    core.set_pause(False)
    return f"Resumed"


##########################################
# debug
##########################################
@app.post("/log_level")
async def set_console_log_level(request: LogLevelRequest):
    level = request.log_level
    logManager.set_console_log_level(level)
    logManager.trace("trace")
    logManager.debug("debug")
    logManager.info("info")
    logManager.success("success")
    logManager.warning("warning")
    logManager.error("error")
    logManager.critical("critical")
    return f"console log level: {level}"