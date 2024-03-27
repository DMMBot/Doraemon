#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :utils.py
# @Time :2024-3-27 下午 06:16
# @Author :Qiao
import re
import json
import random
from typing import Any, Union

import nonebot
from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot
from nonebot.matcher import Matcher

from doraemon.utils import *
from .path import *

dirs: List[Path] = [
    config_path
]


async def init():
    """
    启动函数,用于初始化插件所需的一些必要文件
    """
    # 获取机器人
    bots: Dict[str, Bot] = nonebot.get_bots()
    # 循环检查路径是否存在
    [await mk('dir', _, mode=None) for _ in dirs if not _.exists()]

    if not meditationc_path.exists():
        # 如果冥想配置文件未初始化
        meditationc_dict: dict = {}
        # 为每个功能生成默认开关设置
        default_meditaitonc: dict = {
            'state': False,
            'info_state': True,
            'min_time': 60,
            'max_time': 2_592_000
        }
        # 输出日志
        logger.info('正在创建冥想配置文件')
        # 遍历所有机器人实例，获取群组列表
        for bot in bots.values():
            group_list: List[Dict[str, Any]] = await bot.get_group_list()
            # 遍历群组，并使用默认设置初始化每个群组的冥想配置
            # 使用字典推导式来初始化 配置文件
            meditationc_dict: dict = {
                str(group['group_id']): default_meditaitonc.copy() for group in group_list
            }
        json_write(meditationc_path, meditationc_dict)

    logger.info('娱乐插件 初始化检测完成')


def parse_seconds(seconds):
    """
    将秒转换为时间
    """
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return f"{days}天 {hours}小时 {minutes}分钟"


def parse_time_input(input_str) -> int:
    """
    处理输入的时间，转换成秒
    """
    try:
        input_str = json.loads(input_str)["message"][-1]["data"]["text"]
        # 通过正则表达式找到所有符合模式的项
        matches = re.findall(r'(\d+)([天时分秒])', input_str)
        # 直接计算总秒数
        total_seconds = sum(
            int(num) * {'秒': 1, '分': 60, '时': 3600, '天': 86400}[unit] for num, unit in matches
        )
        # 检查总秒数是否符合范围（不能低于1分钟且不能超过30天）
        if 60 <= total_seconds <= 2_592_000:
            return total_seconds
        else:
            return '时间参数不对喔, 最小值为一分钟, 最大值为30天'
    except KeyError:
        return '缺少时间参数喔'
