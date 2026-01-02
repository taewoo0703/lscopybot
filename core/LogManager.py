from utility.BaseLogManager import BaseLogManager, log_level_under
from settings import settings
from typing import Literal
from dhooks import Embed

class LogManager(BaseLogManager):
    def __init__(self, discord_webhook_url: str | None = None):
        super().__init__(discord_webhook_url)


    # @log_level_under("TRACE")
    # async def log_order_message_async(self, order_info: OrderRequest):
    #     content = f"거래소\n{order_info.exchange}\n\n심볼\n{order_info.unified_symbol}\n\n거래유형\n{order_info.side}\n\n{order_info.amount}"
    #     embed = Embed(
    #         title=order_info.order_name,
    #         description=f"체결: {order_info.exchange} {order_info.unified_symbol} {order_info.side} {order_info.amount}",
    #         color=0x0000FF,
    #     )
    #     embed.add_field(name="거래소", value=order_info.exchange, inline=False)
    #     embed.add_field(name="심볼", value=order_info.unified_symbol, inline=False)
    #     embed.add_field(name="거래유형", value=order_info.side, inline=False)
    #     embed.add_field(name="수량", value=str(order_info.amount), inline=False)
    #     embed.add_field(name="가격", value=str(order_info.price), inline=False)
    #     await self.log_message_async(content, embed)

    # @log_level_under("ERROR")
    # async def log_order_error_message_async(self, error: str | Exception, order_info: OrderRequest):
    #     """
    #     주문 에러 메시지
    #     """
    #     if isinstance(error, Exception):
    #         error = self.get_error(error)

    #     embed = Embed(
    #         title=f"{order_info.order_name} 에러",
    #         description=f"[[{order_info.exchange}] {order_info.base} 에러가 발생했습니다]\n{error}",
    #         color=0xFF0000,
    #     )
    #     await self.log_message_async(embed=embed)


# singleton
logManager = LogManager(settings.DISCORD_WEBHOOK_URL)
