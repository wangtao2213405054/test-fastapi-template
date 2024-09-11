# _author: Coke
# _date: 2024/7/25 13:44
# _description: 工具集合

import json
import os
import random
import string
from collections import Counter
from typing import Any

import pypinyin

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    """
    返回一个指定长度的随机字符串

    :param length: 需要返回的长度
    :return: 指定长度的随机字母数字字符串
    """
    return "".join(random.choices(ALPHA_NUM, k=length))


def analysis_json(filepath: str) -> dict | list:
    """
    将 JSON 文件进行解析

    :param filepath: 文件路径
    :return: 解析后的字典或列表
    """
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


def join_path(*args: str) -> str:
    """
    获取项目基础绝对路径, 从项目根目录(src)出发

    :param args: 要拼接的目录名称
    :return: 拼接后的绝对路径
    """
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), *args))


def create_dir(dir_path: str) -> str:
    """
    创建指定目录

    :param dir_path: 目录地址
    :return: 创建的目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def pinyin(chinese_characters: str) -> str:
    """
    将汉字转换为拼音

    :param chinese_characters: 汉字
    :return: 转换后的拼音字符串，每个拼音的首字母大写
    """
    _pinyin = ""
    for item in pypinyin.pinyin(chinese_characters, style=pypinyin.NORMAL):
        _pinyin += "".join(item).capitalize()
    return _pinyin


def get_duplicates(lst: list[Any]) -> list[Any]:
    """
    获取列表中的重复数据
    :param lst:
    :return:
    """
    count = Counter(lst)
    return [item for item, count in count.items() if count > 1]
