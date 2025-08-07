from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from app.utils.error_message import ErrorMessage


def http_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": str(exc)}
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": ErrorMessage.PARAM_ERROR, "details": exc.errors()}
    )


def raise_error(status_code: int, message: str, error: dict = None):
    """
    對應 Node 的 errorMessage(status, message, error) 功能
    """
    raise HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": error
        } if error else message
    )