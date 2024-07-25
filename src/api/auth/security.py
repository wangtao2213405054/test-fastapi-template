import bcrypt


def hash_password(password: str) -> bytes:
    """
    返回一个哈希密码字节流
    :param password: 明文密码
    :return:
    """
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


def check_password(password: str, password_in_db: bytes) -> bool:
    """
    验证密码是否和数据库中的密码匹配
    :param password: 明文密码
    :param password_in_db: 已哈希的密码
    :return:
    """
    password_bytes = bytes(password, "utf-8")
    return bcrypt.checkpw(password_bytes, password_in_db)
