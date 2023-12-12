# _author: Coke
# _date: 2023/12/11 23:00

from sqlmodel import SQLModel, Field

from datetime import datetime


class BaseModel(SQLModel):
    """ 基础模型 """
    createTime: datetime = Field(default_factory=datetime.now)  # 记录的创建时间
    updateTime: datetime = Field(default_factory=datetime.now)  # 记录的更新时间
