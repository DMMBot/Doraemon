#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName :path.py
# @Time :2024-3-9 下午 11:04
# @Author :Qiao
from pathlib import Path
from typing import Dict, List

"""
用于存放所有群的相关配置文件路径,按照文件类型分类
"""

config_path = Path() / 'config'  # 插件配置文件路径 - 一切的基础
switcher_path = config_path / 'switch_config.json'  # 群配置开关
requests_path = config_path / 'requests_config.json'  # 加群审核配置

admin_funcs: Dict[str, List[str]] = {
    'admin': [
        '群管系统', '禁言', '解除禁言', '开启全体禁言', '关闭全体禁言',
        '踢出', '拉黑', '添加管理员', '删除管理员'
    ],
    'requests': [
        '审核系统', '查看所有词条', '添加词条', '删除词条',
        '开启自动审核', '关闭自动审核',
    ],
}

default_disabled_func: list = []
