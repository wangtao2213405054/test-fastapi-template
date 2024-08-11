# _author: Coke
# _date: 2024/7/26 14:15
# _description: 密码加密相关

import base64
from typing import Tuple

import bcrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def generate_rsa_key_pair() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    生成一个 RSA 密钥对

    这个函数生成一个 RSA 密钥对，包括一个私钥和一个公钥。RSA 密钥对用于加密和解密操作。

    :return: 一个包含 RSA 私钥和公钥的元组
        - 第一个元素是 RSA 私钥对象
        - 第二个元素是 RSA 公钥对象
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()
    return private_key, public_key


def serialize_key(key: rsa.RSAPublicKey | rsa.RSAPrivateKey) -> bytes:
    """
    将 RSA 密钥序列化为 PEM 格式

    这个函数将 RSA 密钥序列化为 PEM 格式的字节串，可以将其保存到文件中或传输到其他系统。

    :param key: 要序列化的 RSA 密钥对象
        - 可以是 RSA 私钥对象或公钥对象

    :return: 序列化后的 PEM 格式密钥
        - 以字节串形式返回 PEM 编码的密钥
    """
    if isinstance(key, rsa.RSAPrivateKey):
        # 序列化为 PEM 格式的私钥
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),  # 无加密
        )
    else:
        # 序列化为 PEM 格式的公钥
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )


def decrypt_pem(pem: str) -> PublicKeyTypes:
    """
    将 PEM 格式秘钥转换为 RSA 秘钥

    :param pem: 序列化后的 PEM 格式密钥

    :return: RSA 秘钥
    """
    return load_pem_public_key(pem.encode("utf-8"))


def encrypt_message(public_key: rsa.RSAPublicKey, message: str) -> str:
    """
    使用 RSA 公钥加密消息

    这个函数使用给定的 RSA 公钥对消息进行加密。加密后的消息使用 Base64 编码，以便于传输和存储。

    :param public_key: RSA 公钥对象，用于加密消息
    :param message: 要加密的消息，必须是字符串格式
    :return: 加密后的消息，Base64 编码的字符串格式
        - 返回的字符串可以安全地进行传输和存储
    """
    encrypted_message = public_key.encrypt(
        message.encode("utf-8"),  # 将消息转换为字节串
        padding.PKCS1v15(),
    )

    return base64.b64encode(encrypted_message).decode("utf-8")  # 使用 Base64 编码后返回字符串


def decrypt_message(private_key: rsa.RSAPrivateKey, encrypted_message: str) -> str:
    """
    使用 RSA 私钥解密消息

    这个函数使用给定的 RSA 私钥对加密的消息进行解密。消息必须是 Base64 编码格式。

    :param private_key: RSA 私钥对象，用于解密消息
    :param encrypted_message: 已加密的消息，Base64 编码的字符串格式
    :return: 解密后的消息，字符串格式
        - 返回解密后的明文消息
    """
    decrypted_message = private_key.decrypt(
        base64.b64decode(encrypted_message),  # 先解码 Base64，再进行解密
        padding.PKCS1v15(),
    )
    return decrypted_message.decode("utf-8")  # 将解密后的字节串转换为字符串


def hash_password(password: str) -> bytes:
    """
    返回一个哈希密码字节流

    这个函数将明文密码哈希化以提高安全性，使用 bcrypt 算法进行加密。哈希后的密码可以安全地存储在数据库中。

    :param password: 明文密码，字符串格式
    :return: 已哈希的密码，字节串格式
        - 返回的哈希密码可以存储到数据库中用于后续验证
    """
    pw = bytes(password, "utf-8")  # 将明文密码转换为字节串
    salt = bcrypt.gensalt()  # 生成一个随机盐值
    return bcrypt.hashpw(pw, salt)  # 使用 bcrypt 算法对密码进行哈希


def check_password(password: str, password_in_db: bytes) -> bool:
    """
    验证密码是否和数据库中的密码匹配

    这个函数将明文密码与数据库中存储的哈希密码进行比较，以确认密码是否正确。

    :param password: 明文密码，字符串格式
    :param password_in_db: 已哈希的密码，字节串格式
        - 从数据库中检索到的哈希密码
    :return: 如果密码匹配，返回 True；否则返回 False
        - 返回值用于验证用户登录等操作
    """
    password_bytes = bytes(password, "utf-8")  # 将明文密码转换为字节串
    return bcrypt.checkpw(password_bytes, password_in_db)  # 使用 bcrypt 比较密码
