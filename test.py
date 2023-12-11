from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from src.models import ResponseModel


import uvicorn


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


class DetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


app = FastAPI()


@app.exception_handler(DetailedHTTPException)
async def exception_handler(request: Request, exc: DetailedHTTPException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.STATUS_CODE, "message": exc.detail, "data": None}
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise PermissionDenied()
    return {"unicorn_name": name}


if __name__ == '__main__':
    uvicorn.run("test:app", port=8002)
