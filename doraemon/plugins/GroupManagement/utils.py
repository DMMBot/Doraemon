#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :utils.py
# @Time :2024-3-9 下午 11:14
# @Author :Qiao
import json
import random
import re
from typing import Any, Union

import nonebot
from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot
from nonebot.matcher import Matcher

from .config import global_config, plugin_config
from .path import *

su = global_config.superusers

dirs: List[Path] = [
    config_path
]


async def init():
    """
    启动函数,用于初始化插件所需的一堆必要文件
    """
    # 获取机器人
    bots: Dict[str, Bot] = nonebot.get_bots()
    # 循环检查路径是否存在
    [await mk('dir', _, mode=None) for _ in dirs if not _.exists()]

    if not switcher_path.exists():
        # 如果开关文件未初始化
        switcher_dict: dict = {}

        # 为每个功能生成默认开关设置
        default_switchers: dict = {func_name: False for func_name in admin_funcs}

        # 输出日志
        logger.info('创建开关配置文件,所有配置默认关闭')

        # 遍历所有机器人实例，获取群组列表
        for bot in bots.values():
            group_list: List[Dict[str, Any]] = await bot.get_group_list()
            # 遍历群组，并使用默认设置初始化每个群组的开关配置
            # 使用字典推导式来初始化 配置文件
            switcher_dict: dict = {str(group['group_id']): default_switchers.copy() for group in group_list}

        json_write(switcher_path, switcher_dict)

    if not requests_path.exists():
        # 如果审核配置文件未初始化
        requests_dict: dict = {}

        # 加群审核配置
        default_requests: dict = {'state': False, 'word': []}

        # 输出日志
        logger.info('创建审核配置文件,所有配置默认关闭')

        # 遍历所有机器人实例，获取群组列表
        for bot in bots.values():
            group_list: List[Dict[str, Any]] = await bot.get_group_list()
            # 遍历群组，并使用默认设置初始化每个群组的审核配置
            # 使用字典推导式来初始化 配置文件
            requests_dict: dict = {str(group['group_id']): default_requests.copy() for group in group_list}
        json_write(requests_path, requests_dict)

    logger.info('群管插件 初始化检测完成')


async def mk(type_: str, path_: Path, mode: str, *args, **kwargs):
    """
    用于创建文件/文件夹
    :param type_: ['file', 'dir']
    :param path_: Path
    :param mode: ['w', 'wb']
    :param args:
    :param kwargs: ['content', 'dec', 'info'] 写入内容 描述信息 和 额外信息
    """

    if 'info' in kwargs:
        # 检查是否有额外信息需要输出
        logger.info(kwargs['info'])

    if not mode and type_ == 'file':
        # 检查模式是否为空
        raise KeyError('参数 mode(str) 不能为空')

    if type_ == 'dir':
        # 创建文件夹
        path_.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建文件夹: {path_}")
    elif type_ == 'file':
        # 创建文件
        with open(path_, mode[0]) as file:
            file.write(kwargs['content'])
            logger.info(f'创建文件: {path_}')
    else:
        raise KeyError('参数 type_(str) 应该为 "file" 或者 "dir"')


def parse_time_input(input_str) -> int:
    """
    处理输入的时间，转换成秒
    """
    try:
        input_str = json.loads(input_str)["message"][-1]["data"]["text"]
        # 通过正则表达式找到所有符合模式的项
        matches = re.findall(r'(\d+)(天|小时|分钟)', input_str)
        # 直接计算总秒数
        total_seconds = sum(
            int(num) * {'分钟': 60, '小时': 3600, '天': 86400}[unit] for num, unit in matches
        )
        # 检查总秒数是否超出范围（不能超过30天）
        if total_seconds > 2_592_000:
            return None
        return total_seconds
    except KeyError:
        # 如果不存在时间参数则返回None
        return None


def At(data: str) -> Union[list[str], list[int], list]:
    """
    检测at了谁，返回[qq, qq, qq,...]
    包含全体成员直接返回['all']
    如果没有at任何人，返回[]
    :param data: event.json
    :return: list
    """
    try:
        # 代码源自 yzyyz1387/nonebot_plugin_admin 项目，此处改为推导式
        data = json.loads(data)
        for msg in data['message']:
            if msg['type'] == 'at' and 'all' in str(msg):
                return ['all']
        return [int(msg['data']['qq']) for msg in data['message'] if msg['type'] == 'at']
    except KeyError:
        return []


async def banSb(bot: Bot, gid: int, ban_list: list, time: int = None, scope: list = None):
    """
    构造禁言
    :param bot: 机器人
    :param gid: 群号
    :param time: 时间（s)
    :param ban_list: at列表
    :param scope: 用于被动检测禁言的时间范围
    :return:禁言操作
    """
    if 'all' in ban_list:
        yield bot.set_group_whole_ban(group_id=gid, enable=True)
    else:
        time = random.randint(
            *(scope or (plugin_config.ban_rand_time_min, plugin_config.ban_rand_time_max
                        ))) if time is None else time
        for qq in ban_list:
            if int(qq) in su or str(qq) in su:
                logger.info(f"SUPERUSER无法被禁言, {qq}")
            else:
                yield bot.set_group_ban(group_id=gid, user_id=qq, duration=time)


def MsgText(data: str):
    """
    返回消息文本段内容(即去除 cq 码后的内容)
    :param data: event.json()
    :return: str
    """
    try:
        data = json.loads(data)
        # 过滤出类型为 text 的【并且过滤内容为空的】
        msg_text_list = filter(
            lambda x: x['type'] == 'text' and x['data']['text'].replace(' ', '') != '',
            data['message']
        )
        # 拼接成字符串并且去除两端空格
        msg_text = ' '.join(map(lambda x: x['data']['text'].strip(), msg_text_list)).strip()
        return msg_text
    except Exception:
        return ''


async def finish(cmd: Matcher, msg) -> None:
    await cmd.finish(msg)


async def log_finish(cmd: Matcher, msg, log: str = None, err=False) -> None:
    # 输出到日志并finish
    (logger.error if err else logger.info)(log if log else msg)
    await finish(cmd, msg)


def json_write(path: Path | str, data: dict) -> None:
    """
    写入json文件
    """
    with open(path, 'w', encoding='utf-8') as file:
        # 将设置写入文件
        json.dump(data, file, indent=4, ensure_ascii=False)


def json_load(path) -> dict:
    """
    加载json文件
    :return: Optional[dict]
    """
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            contents = json.load(f)
            return contents
    except FileNotFoundError:
        return None


def json_upload(path, dict_content) -> None:
    """
    更新json文件
    :param path: 路径
    :param dict_content: python对象，字典
    """
    with open(path, mode='w', encoding='utf-8') as f:
        f.write(json.dumps(dict_content, ensure_ascii=False, indent=4))
