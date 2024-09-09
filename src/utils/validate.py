# _author: Coke
# _date: 2024/7/25 13:46
# _description: 校验规则

import re


def password(value: str) -> bool:
    """
    校验密码是否符合规则

    :param value: 密码
    :return:
    """

    password_pattern = re.compile(r"^[a-zA-Z0-9]{6,18}$")

    return bool(re.match(password_pattern, value))


def phone_number(mobile: str) -> bool:
    """
    判断是否为手机号（1 开头）

    :param mobile: 手机号
    :return:
    """
    mobile_pattern = r"^(?:(?:\+|00)86)?1\d{10}$"

    return bool(re.match(mobile_pattern, mobile))
