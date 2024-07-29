# _author: Coke
# _date: 2024/7/26 14:15
# _description: 密码加密相关

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from typing import Tuple

import bcrypt
import base64


def generate_rsa_key_pair() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    生成一个 RSA 密钥对

    :return: 一个包含 RSA 私钥和公钥的元组
    """
    # 创建一个 RSA 私钥对象
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # 公钥指数
        key_size=2048,  # 密钥大小
    )
    # 从私钥对象生成公钥对象
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_key(key, is_private: bool = True) -> bytes:
    """
    将 RSA 密钥序列化为 PEM 格式

    :param key: 要序列化的 RSA 密钥对象
    :param is_private: 是否序列化为私钥格式
    :return: 序列化后的 PEM 格式密钥
    """
    if is_private:
        # 序列化为私钥 PEM 格式
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),  # 无加密
        )
    else:
        # 序列化为公钥 PEM 格式
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )


def encrypt_message(public_key: rsa.RSAPublicKey, message: str) -> str:
    """
    使用 RSA 公钥加密消息

    :param public_key: RSA 公钥对象
    :param message: 要加密的消息，字节串格式
    :return: 加密后的消息，字节串格式
    """
    encrypted_message = public_key.encrypt(
        message.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Mask Generation Function
            algorithm=hashes.SHA256(),  # 使用 SHA256 哈希算法
            label=None,
        ),
    )

    return base64.b64encode(encrypted_message).decode("utf-8")


def decrypt_message(private_key: rsa.RSAPrivateKey, encrypted_message: str) -> str:
    """
    使用 RSA 私钥解密消息

    :param private_key: RSA 私钥对象
    :param encrypted_message: 要解密的消息，字节串格式
    :return: 解密后的消息，字节串格式
    """
    decrypted_message = private_key.decrypt(
        base64.b64decode(encrypted_message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Mask Generation Function
            algorithm=hashes.SHA256(),  # 使用 SHA256 哈希算法
            label=None,
        ),
    )
    return decrypted_message.decode("utf-8")


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


if __name__ == "__main__":
    private_key, public_key = generate_rsa_key_pair()
    _message = "this is a test message"
    # 加密
    encrypted_message = encrypt_message(public_key, _message)
    print(encrypted_message)

    # 解密
    decrypted_message = decrypt_message(private_key, encrypted_message)
    print(decrypted_message)
