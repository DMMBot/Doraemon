from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11.message import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="Weather",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

weather = on_command(
    "天气", aliases={"weather", "查天气"}, priority=10, block=True
)


@weather.handle()
async def weather_hendle(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("location", args)


@weather.got("location", "请输入地名")
async def got_location(location: str = ArgPlainText()):
    if location in ["东京", "首尔"]:
        await weather.reject(f"抱歉,{location}的天气暂不支持查询,请重新输入")
    await weather.finish(f"今天{location}的天气是")
