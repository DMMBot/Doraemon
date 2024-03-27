#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :path.py
# @Time :2024-3-27 下午 06:16
# @Author :Qiao
from pathlib import Path
from typing import Dict, List

"""
用于存放所有群的相关配置文件路径,按照文件类型分类
"""

config_path = Path() / 'config/Amuse'  # 插件配置文件路径 - 一切的基础
meditationc_path = config_path / 'meditationc_path.json'  # 冥想功能配置

amuse_funcs: Dict[str, List[str]] = {
    'meditationc': [
        '冥想配置', '打开冥想', '关闭冥想',
        '打开冥想提示', '关闭冥想提示',
        '设置最小冥想时长', '设置最大冥想时长', '冥想'
    ]
}

default_disabled_func: list = []
