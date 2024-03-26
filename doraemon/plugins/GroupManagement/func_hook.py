#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :func_hook.py
# @Time :2024-3-25 下午 10:42
# @Author :Qiao
"""
功能钩子函数
"""
import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    ActionFailed,
    GroupMessageEvent,
    Event,
    HonorNotifyEvent,
    GroupUploadNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupAdminNoticeEvent,
    GroupRecallNoticeEvent,
    LuckyKingNotifyEvent
)
from nonebot.matcher import Matcher
from nonebot.message import IgnoredException, run_preprocessor

from .config import global_config
from .path import *
from .switcher import switcher_integrity_check
from .utils import json_load

su = global_config.superusers
admin_path = Path(__file__).parts[-2]

EVENT = (
    GroupMessageEvent,
    GroupUploadNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupAdminNoticeEvent,
    GroupRecallNoticeEvent
)


@run_preprocessor
async def _(bot: Bot, matcher: Matcher, event: Event):
    # 获取插件
    module = str(matcher.module_name).split('.')
    if len(module) < 2 or module[-2] != admin_path:
        # 如果不是本插件则返回
        return
    which_module = module[-1]
    # 获取群号
    gid = event.group_id
    if isinstance(event, EVENT):
        try:
            if which_module not in admin_funcs:
                return
            status = await check_func_status(which_module, str(gid))
            if not status:
                await bot.send_group_msg(
                    group_id=gid,
                    message=f"功能处于关闭状态，发送【开关 {which_module}】开启"
                )
                raise IgnoredException('未开启此功能...')

        except ActionFailed:
            pass
        except FileNotFoundError:
            pass


async def check_func_status(func_name: str, gid: str) -> bool:
    """
    检查某个群的某个功能是否开启
    :param func_name: 功能名
    :param gid: 群号
    :return: bool
    """
    funcs_status = json_load(switcher_path)
    if funcs_status is None:
        raise FileNotFoundError(switcher_path)
    try:
        return bool(funcs_status[gid][func_name])
    except KeyError:  # 新加入的群
        bots = nonebot.get_bots()
        for bot in bots.values():
            await switcher_integrity_check(bot)
        return False  # 直接返回 false
