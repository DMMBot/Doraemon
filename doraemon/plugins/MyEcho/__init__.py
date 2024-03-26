from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata


from .config import Config

__plugin_meta__ = PluginMetadata(
    name="echo",
    description="",
    usage="",
    config=None,
)

# config = get_plugin_config(Config)


echo = on_command("echo")


@echo.handle()
async def handle_echo(message: Message = CommandArg()):
    if any((not seg.is_text()) or str(seg) for seg in message):
        await echo.send(message=message)
