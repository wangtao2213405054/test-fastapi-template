
from fastapi import FastAPI, Body
from pydantic import Field, BaseModel
from typing import TypeVar, Generic

import uvicorn

app = FastAPI()


class LoginRequest(BaseModel):
    username: str = Body(..., description="用户名", min_length=6, max_length=32)
    password: str = Body(..., title="")


class LoginResponse(BaseModel):
    token: str


T = TypeVar("T")


class Code(BaseModel, Generic[T]):
    code: int = Field(1)
    message: str = Field("接口请求成功")
    data: T = Field(None)


class Test(Code):
    data: LoginResponse


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/hello/{name}")
async def say_hello(name: str, item: LoginRequest) -> Test:
    print(item, '111')

    return Test(token=name)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
