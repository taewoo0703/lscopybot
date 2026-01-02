from fastapi.exception_handlers import request_validation_exception_handler
from fastapi import FastAPI, Request, status, BackgroundTasks, Query
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import traceback, ipaddress, asyncio, os, json, httpx

from settings import settings
from protocol import *
from core import *



# global instance
VERSION = "LS Copy Bot ver 1.0"
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
app = FastAPI(default_response_class=ORJSONResponse)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

##############################
# routing
##############################
@app.get("/params")
async def get_params():
    return RedirectResponse(url="/static/params.html")

@app.get("/monitoring")
async def get_monitoring():
    return RedirectResponse(url="/static/monitoring.html")

@app.get("/admin")
async def get_admin():
    return RedirectResponse(url="/static/admin.html")

##############################
# fundamental functinos
##############################
@app.on_event("startup")
async def startup():    
    # initialize log manager
    logManager.initialize()
    
    # initialize core
    await core.initialize()

    # initialize done
    await logManager.log_message_async(f"LS Copy Bot 실행 완료! - 버전: {VERSION}")



@app.on_event("shutdown")
async def shutdown():
    await core.on_shutdown()

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
    pass
    # exchange_name = request.exchange_name
    # symbol_list = core.get_symbol_list(exchange_name)

    # result = {}
    # if not settings.IS_SLAVE:
    #     # master
    #     result[exchange_name] = {"master": symbol_list}
    #     if settings.SLAVE_DOMAINS:
    #         for slave_domain in settings.SLAVE_DOMAINS:
    #             result[exchange_name] |= {slave_domain: await get_slave_symbols(slave_domain, request)}
    # else:
    #     # slave
    #     result = {exchange_name: symbol_list}

    # return result

@app.post("/view_params")
async def view_params(request: BaseRequest):
    pass
    # betting_params = core.get_betting_params(exchange_name)

    # result = {}
    # if not settings.IS_SLAVE:
    #     # master
    #     result[exchange_name] = {"master": {"indicator_params": indicator_params, "signal_params": signal_params, "betting_params": betting_params}}
    #     if settings.SLAVE_DOMAINS:
    #         for slave_domain in settings.SLAVE_DOMAINS:
    #             result[exchange_name] |= {slave_domain: await get_slave_params(slave_domain, request)}
    # else:
    #     # slave
    #     result = {exchange_name: {"indicator_params": indicator_params, "signal_params": signal_params, "betting_params": betting_params}}
        
    # return result


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
# @app.post("/pause")
# async def pause_hatiko(request: BaseRequest):
#     exchange_name = request.exchange_name
#     core.pause_hatiko(exchange_name)
#     return True

# @app.post("/resume")
# async def resume_hatiko(request: BaseRequest):
#     exchange_name = request.exchange_name
#     core.resume_hatiko(exchange_name)
#     return True


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