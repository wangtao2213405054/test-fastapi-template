# _author: Coke
# _date: 2024/8/1 下午5:18
# _description:

from pydantic import BaseModel

from src.api.auth.models.models import AffiliationInfoResponse


class InitDataBase(BaseModel):
    affiliation: AffiliationInfoResponse
