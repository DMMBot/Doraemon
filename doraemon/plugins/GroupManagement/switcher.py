#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :switcher.py
# @Time :2024-3-25 下午 09:13
# @Author :Qiao
"""
管理插件功能开关
"""
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .path import admin_funcs, switcher_path, default_disabled_func
from .utils import json_load, json_upload, finish

oepn = on_command(
    '开启', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@oepn.handle()
async def _(
        bot: Bot, matcher: Matcher, event: GroupMessageEvent,
        args: Message = CommandArg()
):
    gid = str(event.group_id)
    user_input_func_name = str(args)
    try:
        await switcher_handle(gid, matcher, user_input_func_name, True)
    except KeyError:
        # 如果配置文件更新不及时引发了 KeyError 则检查配置文件
        await switcher_integrity_check(bot)
        await switcher_handle(gid, matcher, user_input_func_name, True)


off = on_command(
    '关闭', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@off.handle()
async def _(
        bot: Bot, matcher: Matcher, event: GroupMessageEvent,
        args: Message = CommandArg()
):
    gid = str(event.group_id)
    user_input_func_name = str(args)
    try:
        await switcher_handle(gid, matcher, user_input_func_name, False)
    except KeyError:
        # 如果配置文件更新不及时引发了 KeyError 则检查配置文件
        await switcher_integrity_check(bot)
        await switcher_handle(gid, matcher, user_input_func_name, False)


async def switcher_integrity_check(bot: Bot):
    """
    配置文件校验器
    """
    # 获取机器人所有群组列表
    group_list = await bot.get_group_list()
    # 加载配置文件
    switcher_dict = json_load(switcher_path)

    for group in group_list:
        gid = str(group['group_id'])
        # 如果群组在开关设置中不存在，则初始化该群组的设置
        if gid not in switcher_dict:
            switcher_dict[gid] = {func: False for func in admin_funcs}
        else:
            # 如果群组在开关设置中存在，则检查是否有新功能需要添加
            this_group_switcher = switcher_dict[gid]
            for func in admin_funcs:
                # 如果发现新功能没有设置，则加入该新功能的默认设置
                if func not in this_group_switcher:
                    this_group_switcher[func] = func not in default_disabled_func

    # 检查完成后更新配置文件
    json_upload(switcher_path, switcher_dict)


async def switcher_handle(gid: str, matcher: Matcher, func: str, state):
    """
    设置群管功能函数
    """
    if func in admin_funcs:
        # 如果用户输入功能是插件功能,获取插件配置文件
        funcs_status = json_load(switcher_path)
        if state:
            funcs_status[gid][func] = state
            json_upload(switcher_path, funcs_status)
            await finish(matcher, f'已开启 {func}')
        else:
            funcs_status[gid][func] = state
            json_upload(switcher_path, funcs_status)
            await finish(matcher, f'已关闭 {func}')
