# _author: Coke
# _date: 2024/7/25 13:44
# _description: 工具集合

from typing import Union
import logging
import random
import string
import json


logger = logging.getLogger(__name__)
ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    """
    返回一个指定长度的随机字符串
    :param length: 需要返回的长度
    :return:
    """
    return "".join(random.choices(ALPHA_NUM, k=length))


def analysis_json(filepath) -> Union[dict, list]:
    """
    将 JSON 文件进行解析
    :param filepath: 文件路径
    :return:
    """
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data
