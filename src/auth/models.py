# _author: Coke
# _date: 2023/12/11 23:00

from sqlmodel import Field

from src.models import BaseModel


class UserTable(BaseModel, table=True):
    """ 用户数据库模型 """
    id: int = Field(..., primary_key=True)
    name: str  # 名称
    email: str  # 邮箱 不可重复
    password: str = Column(db.String(512), nullable=False)  # 密码
    mobile: str = Column(db.String(11), unique=True, nullable=False)  # 手机号 不可重复
    avatar_url: str = Column(db.String(512))  # 头像
    state: bool = Column(db.Boolean, nullable=False)  # 用户在职状态
    node: int = Column(db.Integer)  # 节点
    role: int = Column(db.Integer, nullable=False)  # 角色
    department: str = Column(db.String(64))  # 部门


class BaseCreate(UserTable):
    """ 用于创建新的实例 """
