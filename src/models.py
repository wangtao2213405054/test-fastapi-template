# _author: Coke
# _date: 2023/12/11 23:00

from sqlmodel import SQLModel, Field

from datetime import datetime


class BaseModel(SQLModel):
    """ 基础模型 """
    create_time: datetime = Field(default_factory=datetime.now)  # 记录的创建时间
    update_time: datetime = Field(default_factory=datetime.now)  # 记录的更新时间


class Base(BaseModel, table=True):
    """ 数据库模型 """
    id: int = Field(..., primary_key=True)


class BaseCreate(BaseModel):
    """ 用于创建新的实例 """
