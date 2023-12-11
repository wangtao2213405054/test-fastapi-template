import logging
import random
import string

logger = logging.getLogger(__name__)
ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    """
    返回一个指定长度的随机字符串
    :param length: 需要返回的长度
    :return:
    """
    return "".join(random.choices(ALPHA_NUM, k=length))
