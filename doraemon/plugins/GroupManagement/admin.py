#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :admin.py
# @Time :2024-3-10 上午 12:35
# @Author :Qiao
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER

from .config import global_config, plugin_config
from .utils import At, banSb, log_finish, finish, parse_time_input

su = global_config.superusers

info = on_command(
    '群管系统', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@info.handle()
async def _(matcher: Matcher):
    """
    回复可用指令
    """
    menu_msg = Message([
        MessageSegment.text(" "*10),
        MessageSegment.face(319),
        MessageSegment.text('群管系统'),
        MessageSegment.face(319),
        MessageSegment.text("\n\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 禁言 [@user] 时间\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 解除禁言 [@user]\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 开启/关闭全体禁言\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 踢出/拉黑 [@user]\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 添加/删除管理员[@user]\n"),
    ])
    await finish(matcher, menu_msg)


ban = on_command(
    '禁言', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@ban.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    禁言 @user 禁言
    """
    # 提取消息中所有数字作为禁言时间
    time = parse_time_input(event.json())
    scope = (plugin_config.ban_rand_time_min, plugin_config.ban_rand_time_max)
    # 获取操作对象
    sb = At(event.json())

    if not sb:
        await finish(matcher, "未选中需要操作的用户")

    try:
        if time is None:
            async for baned in banSb(bot, event.group_id, ban_list=sb, scope=scope):
                await baned if baned else None
        else:
            async for baned in banSb(bot, event.group_id, ban_list=sb, time=time):
                await baned if baned else None
        await finish(matcher, '禁言操作成功' if time is not None else '参数错误或未填，用户已被禁言随机时长')
    except ActionFailed:
        await finish(matcher, '权限不足')


unban = on_command(
    '解除禁言', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@unban.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    解除禁言 @user
    """
    sb = At(event.json())

    if not sb:
        await finish(matcher, "未选中需要操作的用户")

    try:
        async for baned in banSb(bot, event.group_id, ban_list=sb, time=0):
            await baned if baned else None
        await finish(matcher, '已解除用户禁言')
    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)


ban_all = on_command(
    '开启全体禁言', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@ban_all.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    全体禁言
    """
    try:
        await bot.set_group_whole_ban(
            group_id=event.group_id,
            enable=True
        )
        await finish(matcher, "已开启全体禁言")
    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)


unban_all = on_command(
    '关闭全体禁言', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@unban_all.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    关闭全体禁言
    """
    try:
        await bot.set_group_whole_ban(
            group_id=event.group_id,
            enable=False
        )
        await finish(matcher, "已关闭全体禁言")
    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)


kick = on_command(
    '踢出', priority=1, block=False,
    permission=GROUP_OWNER | SUPERUSER
)


@kick.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    踢出 @user
    """
    sb = At(event.json())

    if not sb:
        await finish(matcher, '未选择操作用户')
    if 'all' in sb:
        await finish(matcher, '不能踢出全体成员')

    try:
        for qq in sb:
            if qq == event.user_id:
                await finish(matcher, '把自己踢了?')
            if qq in su:
                await finish(matcher, '你不能踢出Super User')
            await bot.set_group_kick(
                group_id=event.group_id,
                user_id=qq,
                reject_add_request=False
            )
        await finish(matcher, '踢人操作完成')

    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)


black = on_command(
    '拉黑', priority=1, block=False,
    permission=GROUP_OWNER | SUPERUSER
)


@black.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    拉黑 @user
    """
    sb = At(event.json())

    if not sb:
        await finish(matcher, '未选择操作用户')
    if 'all' in sb:
        await finish(matcher, '不能踢出全体成员')

    try:
        for qq in sb:
            if qq == event.user_id:
                await finish(matcher, '把自己拉黑了?')
            if qq in su:
                await finish(matcher, '你不能拉黑Super User')
            await bot.set_group_kick(
                group_id=event.group_id,
                user_id=qq,
                reject_add_request=True
            )
        await finish(matcher, '踢出并拉黑操作完成')

    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)


set_group_admin = on_command(
    '添加管理员', priority=1, block=False, permission=SUPERUSER
)


@set_group_admin.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    添加管理员 @user
    """
    sb = At(event.json())

    if not sb:
        await finish(matcher, '未选择操作用户')
    if 'all' in sb:
        await finish(matcher, '谁教你这么干的')

    try:
        for qq in sb:
            await bot.set_group_admin(
                group_id=event.group_id,
                user_id=int(qq),
                enable=True
            )
            await finish(matcher, '添加管理员成功')

    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)


unset_group_admin = on_command(
    '删除管理员', priority=1, block=False, permission=SUPERUSER
)


@unset_group_admin.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    g_admin / 上管 @user
    """
    sb = At(event.json())

    if not sb:
        await finish(matcher, '未选择操作用户')
    if 'all' in sb:
        await finish(matcher, '谁教你这么干的')

    try:
        for qq in sb:
            await bot.set_group_admin(
                group_id=event.group_id,
                user_id=int(qq),
                enable=False
            )
            await finish(matcher, '删除管理员成功')

    except ActionFailed as e:
        await log_finish(matcher, '权限不足', log=e, err=True)
