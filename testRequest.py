import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from src.api.auth.security import encrypt_message, hash_password, check_password
import requests


key = requests.request('GET', 'http://127.0.0.1:8000/api/v1/client/auth/public/key')

_key = key.json()["data"]

public_key = serialization.load_pem_public_key(
    _key.encode("utf-8"),
    backend=default_backend()
)


data = requests.request(
    "POST",
    "http://127.0.0.1:8000/api/v1/client/auth/user/login",
    json={
      "username": "usecr@example.com",
      "password": encrypt_message(public_key, "WT1234567!")
    }
)

# data = requests.request(
#     "POST",
#     "http://127.0.0.1:8000/api/v1/client/auth/update/password",
#     json={
#         "newPassword": encrypt_message(public_key, "WT1234567!"),
#         "oldPassword": encrypt_message(public_key, "WT123456!")
#     }
# )


print(data.json())
#
# print(check_password("WT123456!", hash_password("WT123456!")))