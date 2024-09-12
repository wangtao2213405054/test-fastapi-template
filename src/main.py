# _author: Coke
# _date: 2024/7/25 17:05
# _description: 服务主入口, 包含了错误处理、日志、中间件、路由等...

import logging
import time
import traceback
import uuid
from typing import Awaitable, Callable

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.concurrency import iterate_in_threadpool
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.exc import DatabaseError

from src.api.auth.router import router as auth_router
from src.api.manage.router import router as manage_router
from src.api.route.router import router as route_router
from src.cache import lifespan
from src.config import app_configs, settings
from src.exceptions import DetailedHTTPException, message
from src.exceptions import status as _status
from src.models.types import ResponseModel
from src.websocketio import socket_app

# 初始化 Fast Api 并写入接口的 prefix
app = FastAPI(**app_configs, lifespan=lifespan)


# 添加 socketio 事件处理程序
app.mount(settings.SOCKET_PREFIX, socket_app)


# 错误捕获与转发
@app.exception_handler(Exception)
async def passive_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    对非主动抛出的异常进行捕获, 外部状态码为 200, 内部状态码

    :param _request: FastApi <Request> 对象
    :param exc: 错误对象
    :return: 返回错误的堆栈信息、错误信息及标识符. 标识符应用与查找日志信息
    """

    uuid4 = uuid.uuid4()

    error_info = dict(error=str(exc), sign=str(uuid4), stack=traceback.format_exception(exc))
    logging.exception(f"Exception ID: {uuid4}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            ResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message.HTTP_500_INTERNAL_SERVER_ERROR,
                data=error_info if settings.ENVIRONMENT.is_debug else str(uuid4),
            )
        ),
    )


@app.exception_handler(DetailedHTTPException)
async def active_exception_handler(_request: Request, exc: DetailedHTTPException) -> JSONResponse:
    """
    对所有主动抛出的异常做了转发, 所有的状态码都是 200, 并将详细信息填写入返回值信息中

    :param _request: FastApi <Request> 对象
    :param exc: 错误信息, 需要继承<DetailedHTTPException>类
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            ResponseModel(
                code=exc.STATUS_CODE,
                message=exc.DETAIL,
                data=exc.ERRORS if settings.ENVIRONMENT.is_debug else None,  # 只有在 DEBUG 模式才返回详细的错误信息
            )
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    对入参错误异常做了转发, 当前响应码为 200, 并将错误信息返回至data 中
    jsonable_encoder 会将数据类型转换成 JSON兼容类型
    exc 的 ctx 可能会出现对象, 我们需要调用这个方法来兼容

    :param _request: FastApi <Request> 对象
    :param exc: <RequestValidationError>类
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            ResponseModel(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message=message.HTTP_422_UNPROCESSABLE_ENTITY,
                data=dict(body=exc.body, detail=jsonable_encoder(exc.errors()))
                if settings.ENVIRONMENT.is_debug
                else None,
            )
        ),
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(_request: Request, exc: DatabaseError) -> JSONResponse:
    """
    捕获 SQLAlchemy 抛出的 DatabaseError 并将结果转换成 JSON 返回

    :param _request: FastApi <Request> 对象
    :param exc: <DatabaseError> 类
    :return:
    """
    exc.orig = str(exc.orig)  # type: ignore
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            ResponseModel(
                code=_status.DATABASE_600_BAD_SQL,
                message=message.DATABASE_600_BAD_SQL,
                data=jsonable_encoder(exc) if settings.ENVIRONMENT.is_debug else None,
            )
        ),
    )


# 添加 CORS（跨源资源共享）中间件 忽略 PyCharm 的警告信息, 由于他们是正确的
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


@app.middleware("http")
async def http_middleware(
    request: Request, callback: Callable[[Request], Awaitable[StreamingResponse]]
) -> JSONResponse | StreamingResponse:
    """
    HTTP 中间件, 用于记录请求信息和响应信息

    :param request: 请求信息 FastAPI <Request> 对象
    :param callback: 回调函数
    :return:
    """

    start_time = time.time()

    # request
    body = await request.body()

    client = request.client

    host = client.host if client else "暂无主机信息"
    port = client.port if client else "暂无端口信息"
    logging.info(f'Request Info: {host}:{port} - "{request.method} {request.url.path}"')
    logging.debug(f"Request Headers: {request.headers.items()}")
    logging.info(f"Request Body: {"".join(body.decode("utf-8").split())}")

    # response
    response = await callback(request)

    response_body = [chunk async for chunk in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))

    first_chunk = response_body[0]
    if isinstance(first_chunk, bytes):
        first_chunk = first_chunk.decode("utf-8")

    logging.info(f"Response Body: {first_chunk}")
    logging.info(f"Response Time: {round((time.time() - start_time) * 1000, 3)} ms")

    return response


# 部署环境下打开 Sentry 服务 用于错误跟踪和监控
if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)


app.include_router(auth_router, prefix=settings.PREFIX, tags=["认证"])

app.include_router(manage_router, prefix=settings.PREFIX, tags=["系统管理"])

app.include_router(route_router, prefix=settings.PREFIX, tags=["路由"])
