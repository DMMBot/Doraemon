import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config
from .utils import init

from . import (
    meditationc
)

__plugin_meta__ = PluginMetadata(
    name="Amuse",
    description="机器人基础娱乐功能",
    usage='',
    config=Config,
)

config = get_plugin_config(Config)
driver = nonebot.get_driver()


@driver.on_bot_connect
async def _(bot: nonebot.adapters.Bot):
    await init()
