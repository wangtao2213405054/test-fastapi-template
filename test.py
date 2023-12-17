from typing import List, Optional
from pydantic import BaseModel, Field


# 创建递归模型
class Item(BaseModel):
    name: str


class Mo(BaseModel):
    name: str
    children: list[Item]


# 使用递归模型
data = {
    "name": "Item 1",
    "children": [
        {"name": "Item 1.1"},
        {"name": "Item 1.2", "children": [{"name": "Item 1.2.1"}]}
    ]
}

# 从字典创建模型实例
item = Mo(**data)
print(item)
