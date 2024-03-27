#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :meditationc.py
# @Time :2024-3-27 下午 06:43
# @Author :Qiao
import random

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER

from .utils import *
from .path import *

info = on_command(
    '冥想配置', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@info.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    """
    回复当前群冥想配置
    """
    gid = str(event.group_id)
    config_dict = json_load(meditationc_path)
    state = '已开启' if config_dict[gid]['state'] else '未开启'
    info_state = '已开启' if config_dict[gid]['info_state'] else '未开启'
    min_time = parse_seconds(config_dict[gid]['min_time'])
    max_time = parse_seconds(config_dict[gid]['max_time'])

    menu_msg = Message([
        MessageSegment.text(" " * 12),
        MessageSegment.face(319),
        MessageSegment.text('冥想配置'),
        MessageSegment.face(319),
        MessageSegment.text("\n\n"),
        MessageSegment.face(74),
        MessageSegment.text(f" 是否开启: {state}\n"),
        MessageSegment.face(74),
        MessageSegment.text(f" 是否开启操作通知: {info_state}\n"),
        MessageSegment.face(74),
        MessageSegment.text(f" 最小时间: {min_time}\n"),
        MessageSegment.face(74),
        MessageSegment.text(f" 最大时间: {max_time}\n\n"),
        MessageSegment.text(" " * 12),
        MessageSegment.face(319),
        MessageSegment.text('可用指令'),
        MessageSegment.face(319),
        MessageSegment.text("\n\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 打开/关闭冥想\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 打开/关闭提示\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 设置最大/小冥想时长\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 时长格式: %天%时%分\n"),
    ])

    await finish(matcher, menu_msg)


open_meditationc = on_command(
    '打开冥想', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@open_meditationc.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    打开冥想
    """
    await _set_meditationc_config(
        bot, str(event.group_id), matcher, state=True, set_state=True
    )


off_meditationc = on_command(
    '关闭冥想', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@off_meditationc.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    关闭冥想
    """
    await _set_meditationc_config(
        bot, str(event.group_id), matcher, state=False, set_state=True
    )


open_info = on_command(
    '打开提示', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@open_info.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    打开冥想
    """
    await _set_meditationc_config(
        bot, str(event.group_id), matcher, state=True, set_info=True
    )


off_info = on_command(
    '关闭提示', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@off_info.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    关闭冥想
    """
    await _set_meditationc_config(
        bot, str(event.group_id), matcher, state=False, set_info=True
    )


set_min_time = on_command(
    '设置最小冥想时长', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@set_min_time.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    设置最小冥想时长
    """
    time = parse_time_input(event.json())
    if not isinstance(time, int):
        await finish(matcher, time)
    else:
        await _set_meditationc_config(
            bot, str(event.group_id), matcher, time=time, set_min_time=True
        )


set_max_time = on_command(
    '设置最大冥想时长', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@set_max_time.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent, ):
    """
    设置最小冥想时长
    """
    time = parse_time_input(event.json())
    if not isinstance(time, int):
        await finish(matcher, time)
    else:
        await _set_meditationc_config(
            bot, str(event.group_id), matcher, time=time, set_max_time=True
        )


meditationc = on_command('冥想', priority=1, block=True)


@meditationc.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    冥想
    """
    # TODO 需要做hook监测冥想功能是否开启
    gid = str(event.group_id)
    user_id = event.user_id
    config_dict = json_load(meditationc_path)
    min_time = config_dict[gid]['min_time']
    max_time = config_dict[gid]['max_time']
    time = random.randint(min_time, max_time)
    info_state = config_dict[gid]['info_state']

    try:
        await bot.set_group_ban(group_id=int(gid), user_id=user_id, duration=time)
        if info_state:
            await finish(matcher, f'成功进入冥想状态, 此次冥想时长 {parse_seconds(time)}')
    except ActionFailed:
        await finish(matcher, f'机器人权限不足')


async def _set_meditationc_config(
        bot: Bot, gid: str, matcher: Matcher, state: bool = None,
        time: int = None, set_state=False, set_info=False,
        set_max_time=False, set_min_time=False
):
    """
    设置配置文件
    """

    try:
        config_dict = json_load(meditationc_path)
        if set_state:
            config_dict[gid]['state'] = state
        elif set_info:
            config_dict[gid]['info_state'] = state
        elif set_max_time:
            config_dict[gid]['max_time'] = time
        elif set_min_time:
            config_dict[gid]['min_time'] = time
        json_upload(meditationc_path, config_dict)
        await finish(matcher, '配置成功!')
    except KeyError:
        await meditationc_integrity_check(bot)
        await finish(matcher, '未找到配置项,已重新创建配置项,请重新输入指令')


async def meditationc_integrity_check(bot: Bot):
    """
    配置文件校验器
    """
    # 获取机器人所有群组列表
    group_list = await bot.get_group_list()
    # 加载配置文件
    meditationc_dict = json_load(meditationc_path)

    for group in group_list:
        gid = str(group['group_id'])
        # 如果群组在配置设置中不存在，则初始化该群组的设置
        if gid not in meditationc_dict:
            meditationc_dict[gid] = {
                'state': False,
                'info_state': True,
                'min_time': 60,
                'max_time': 2_592_000
            }

    # 检查完成后更新配置文件
    json_upload(meditationc_path, meditationc_dict)
