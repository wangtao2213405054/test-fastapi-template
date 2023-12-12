
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from src.auth.router import router as auth_router

from src.exceptions import DetailedHTTPException
from src.schemas import ResponseModel

import uvicorn


# 初始化 Fast Api 并写入接口的 prefix
app = FastAPI()
prefix = "/api/v1/client"


@app.exception_handler(DetailedHTTPException)
async def exception_handler(_, exc: DetailedHTTPException):
    """
    对所有的异常做了转发, 所有的状态码都是 200, 并将详细信息填写入返回值信息中
    :param _: FastApi <Request> 对象
    :param exc: 错误信息, 需要继承<DetailedHTTPException>类
    :return:
    """
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(ResponseModel(code=exc.STATUS_CODE, message=exc.DETAIL))
    )


# 路由注册区域
app.include_router(auth_router, prefix=prefix, tags=["认证"])


if __name__ == '__main__':
    uvicorn.run("src.main:app")
