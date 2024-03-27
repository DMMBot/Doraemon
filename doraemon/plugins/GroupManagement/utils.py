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

from doraemon.utils import *
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
        # TODO 未来考虑兼容多机器人
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


