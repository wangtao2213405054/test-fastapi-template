# _author: Coke
# _date: 2023/12/11 21:31

import requests

base_url = "http://localhost:8000"


body = dict(
    username="admin1",
    password=""
)
data = requests.request("POST", base_url + "/api/v1/client/auth/user/login", json=body)

print(data.json())
