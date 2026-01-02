import uvicorn
import fire
from settings import settings
from main import app
import platform, asyncio

def start_server(host="0.0.0.0", port=8000 if settings.PORT is None else settings.PORT):
    # Windows 환경에서 SelectorEventLoop 설정
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app.state.port = port
    uvicorn.run("main:app", host=host, port=port, reload=False, limit_concurrency=1000)


if __name__ == "__main__":
    fire.Fire(start_server)