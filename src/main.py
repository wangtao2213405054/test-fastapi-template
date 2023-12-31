
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from src.exceptions import DetailedHTTPException
from src.schemas import ResponseModel
from src.config import app_configs, settings
from src.cache import lifespan
from starlette.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.websocketio import socket_app

import sentry_sdk
import uvicorn


# 初始化 Fast Api 并写入接口的 prefix
app = FastAPI(**app_configs, lifespan=lifespan)
prefix = "/api/v1/client"

# 添加 socketio 事件处理程序
app.mount("/socket", socket_app)


# 错误捕获与转发
@app.exception_handler(DetailedHTTPException)
async def exception_handler(_request, exc: DetailedHTTPException):
    """
    对所有主动抛出的异常做了转发, 所有的状态码都是 200, 并将详细信息填写入返回值信息中
    :param _request: FastApi <Request> 对象
    :param exc: 错误信息, 需要继承<DetailedHTTPException>类
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(
            code=exc.STATUS_CODE,
            message=exc.DETAIL,
            data=exc.ERRORS if settings.ENVIRONMENT.is_debug else None  # 只有在 DEBUG 模式才返回详细的错误信息
        ))
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError):
    """
    对入参错误异常做了转发, 当前响应码为 200, 并将错误信息返回至data 中
    jsonable_encoder 会将数据类型转换成 JSON兼容类型, exc的 ctx 可能会出现对象, 我们需要调用这个方法来兼容
    :param _request: FastApi <Request> 对象
    :param exc: <RequestValidationError>类
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            ResponseModel(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="请求参数错误",
                data=dict(body=exc.body, detail=jsonable_encoder(exc.errors()))
            )
        )
    )


# 添加 CORS（跨源资源共享）中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

# 部署环境下打开 Sentry 服务 用于错误跟踪和监控
if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )


# 路由注册区域
app.include_router(auth_router, prefix=prefix, tags=["认证"])


if __name__ == '__main__':
    uvicorn.run("src.main:app")
