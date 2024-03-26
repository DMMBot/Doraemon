import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from . import (
    admin,
    requests,
    switcher,
    func_hook,
)
from .config import Config
from .utils import init

__plugin_meta__ = PluginMetadata(
    name="GroupManagement",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
driver = nonebot.get_driver()


@driver.on_bot_connect
async def _(bot: nonebot.adapters.Bot):
    await init()
