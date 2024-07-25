# _author: Coke
# _date: 2023/12/11 23:00
from sqlmodel import SQLModel, Field
from src.models.types import convert_datetime_to_gmt
from datetime import datetime
from pydantic import ConfigDict


class BaseModel(SQLModel):
    """ 基础模型 """

    # 应该使用 default_factory=datetime.now 来生成默认时间, 当时没有找到格式化的方法
    createTime: datetime = Field(default_factory=datetime.now, description="创建时间")  # 记录的创建时间
    updateTime: datetime = Field(default_factory=datetime.now, description="更新时间")  # 记录的更新时间

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True
    )
