import bcrypt
import re

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*\d)(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


# 原始密码
password = "Wc1!sss222"

print(bool(re.match(STRONG_PASSWORD_PATTERN, password)))
