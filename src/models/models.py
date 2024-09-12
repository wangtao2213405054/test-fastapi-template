# _author: Coke
# _date: 2024/7/28 00:56
# _description: 基础数据库模型

from datetime import datetime

from pydantic import ConfigDict, field_serializer
from sqlmodel import Field, SQLModel

from src.models.types import convert_datetime_to_gmt


class BaseNoCommonModel(SQLModel):
    """没有任何定义的基础模型"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,  # 允许使用字符串类型前向引用, 即递归调用
    )  # type: ignore


class BaseModel(BaseNoCommonModel):
    """基础模型"""

    # 应该使用 default_factory=datetime.now 来生成默认时间, 当时没有找到格式化的方法
    createTime: datetime = Field(
        default_factory=datetime.now, description="创建时间", schema_extra={"examples": ["2024-07-31 16:07:34"]}
    )  # 记录的创建时间
    updateTime: datetime = Field(
        default_factory=datetime.now, description="更新时间", schema_extra={"examples": ["2024-07-31 16:07:34"]}
    )  # 记录的更新时间

    @field_serializer("createTime", "updateTime")
    def serialize_datetime(self, value: datetime) -> str:
        """
        将 datetime 对象转换为 GMT 格式的字符串

        :param value: datetime 对象
        :return:
        """
        return convert_datetime_to_gmt(value)
