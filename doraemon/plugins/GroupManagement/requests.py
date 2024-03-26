#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :request.py
# @Time :2024-3-25 下午 11:15
# @Author :Qiao
"""
加群自动审批
"""
from nonebot import on_command, on_request
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Arg
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.typing import T_State

from .path import requests_path
from .utils import finish, json_load, json_upload

info = on_command(
    '审核系统', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@info.handle()
async def _(matcher: Matcher):
    """
    回复可用指令
    """
    menu_msg = Message([
        MessageSegment.text(" " * 10),
        MessageSegment.face(319),
        MessageSegment.text('审核系统'),
        MessageSegment.face(319),
        MessageSegment.text("\n\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 查看所有词条\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 添加/删除词条\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 清空所有词条\n"),
        MessageSegment.face(74),
        MessageSegment.text(" 开启/关闭自动审核\n"),
        MessageSegment.text("\n若词条为空且开启自动审核\n则视为无理由加群"),
    ])
    await finish(matcher, menu_msg)


check_word = on_command(
    '查看词条', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@check_word.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    """
    查看当前群内审核词条
    """
    try:
        gid = str(event.group_id)
        request_config = json_load(requests_path)
        word = request_config[gid]["word"]
        word_quantity = len(word)
        # TODO 此处有漏洞,如果词条数量过多,一次性发送会导致达到消息上限
        if not word:
            await finish(matcher, '还没有添加审核词条噢')
        await finish(matcher, f'当前群词条共计 [{word_quantity}] 条:\n{word}')
    except KeyError:
        await requests_integrity_check(bot)
        await finish(matcher, f'此群缺失配置项,已重新初始化配置项,请重新输入指令')


add_word = on_command(
    '添加词条', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@add_word.handle()
async def _(
        bot: Bot, matcher: Matcher, event: GroupMessageEvent,
        args: Message = CommandArg()
):
    """
    添加词条 词条
    """
    gid = str(event.group_id)
    word = str(args)
    word_dict = json_load(requests_path)

    try:
        word_list: list = word_dict[gid]['word']
        if word not in word_list:
            word_list.append(word)
            json_upload(requests_path, word_dict)
            await finish(matcher, f'成功添加 [{word}]')
        else:
            await finish(matcher, '已存在该词条,请勿重复添加喔')
    except KeyError:
        await requests_integrity_check(bot)
        await finish(matcher, f'此群缺失配置项,已重新初始化配置项,请重新输入指令')


del_word = on_command(
    '删除词条', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@del_word.handle()
async def _(
        bot: Bot, matcher: Matcher, event: GroupMessageEvent,
        args: Message = CommandArg()
):
    """
    删除词条 词条
    """
    gid = str(event.group_id)
    word = str(args)
    word_dict = json_load(requests_path)
    word_list: list = word_dict[gid]['word']

    try:
        word_list.remove(word)
        json_upload(requests_path, word_dict)
        await finish(matcher, f'删除 [{word}] 词条成功')
    except ValueError:
        await finish(matcher, f'不存在 [{word}] 词条喔')
    except KeyError:
        await requests_integrity_check(bot)
        await finish(matcher, f'此群缺失配置项,已重新初始化配置项,请重新输入指令')


empty_word = on_command(
    '清空全部词条', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@empty_word.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    """
    清空所有词条
    """
    gid = str(event.group_id)
    config_dict = json_load(requests_path)
    word_list: list = config_dict[gid]['word']
    word_quantity = len(word_list)
    word_list.clear()
    json_upload(requests_path, config_dict)
    await empty_word.finish(f"执行成功! 共删除 [{word_quantity}] 个词条")


open_auto_auditing = on_command(
    '开启自动审核', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@open_auto_auditing.handle()
async def _(
        bot: Bot, matcher: Matcher, event: GroupMessageEvent,
):
    """
    开启自动审核
    """
    gid = str(event.group_id)
    config_dict = json_load(requests_path)

    try:
        config_dict[gid]['state'] = True
        json_upload(requests_path, config_dict)
        await finish(matcher, f'成功将群 [{gid}] 开启自动审核')
    except KeyError:
        await requests_integrity_check(bot)
        await finish(matcher, f'此群缺失配置项,已重新初始化配置项,请重新输入指令')


off_auto_auditing = on_command(
    '关闭自动审核', priority=1, block=True,
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER
)


@off_auto_auditing.handle()
async def _(
        bot: Bot, matcher: Matcher, event: GroupMessageEvent,
):
    """
    关闭自动审核
    """
    gid = str(event.group_id)
    config_dict = json_load(requests_path)

    try:
        config_dict[gid]['state'] = False
        json_upload(requests_path, config_dict)
        await finish(matcher, f'成功将群 [{gid}] 关闭自动审核')
    except KeyError:
        await requests_integrity_check(bot)
        await finish(matcher, f'此群缺失配置项,已重新初始化配置项,请重新输入指令')


def _is_enable(event: GroupRequestEvent):
    return json_load(requests_path)[str(event.group_id)]['state']


request_role = Rule(_is_enable)
requests_hook = on_request(rule=request_role, priority=1, block=True)


@requests_hook.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    """
    加群消息响应器
    """
    gid = str(event.group_id)
    sub_type = event.sub_type
    flag = event.flag
    comment = event.comment
    word_list: list = json_load(requests_path)[gid]['word']

    if not word_list or comment in word_list:
        # 如果词条为空,则视为无理由加群
        # 或者词条正确,同意进群
        await bot.set_group_add_request(
            flag=flag,
            sub_type=sub_type,
            approve=True,
            reason=''
        )
        await requests_hook.finish()

    else:
        # 否则拒绝进群
        await bot.set_group_add_request(
            flag=flag,
            sub_type=sub_type,
            approve=False,
            reason='答案未通过群管验证，可修改答案后再次申请'
        )
        await requests_hook.finish()


async def requests_integrity_check(bot: Bot):
    """
    配置文件校验器
    """
    # 获取机器人所有群组列表
    group_list = await bot.get_group_list()
    # 加载配置文件
    requests_dict = json_load(requests_path)

    for group in group_list:
        gid = str(group['group_id'])
        # 如果群组在开关设置中不存在，则初始化该群组的设置
        if gid not in requests_dict:
            requests_dict[gid] = {'state': False, 'world': []}

    # 检查完成后更新配置文件
    json_upload(requests_path, requests_dict)
