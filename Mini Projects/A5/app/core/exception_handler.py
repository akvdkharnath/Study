import sys
import os
from fastapi import Request
from fastapi.responses import JSONResponse

async def application_exception_handler(request: Request, e: Exception):
    print("Error occured while handeling the request:")
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(f"Exception in file: {fname}")
    print(f"Exception in line: {exc_tb.tb_lineno}")
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {e}")

    print("Exception in user code:")
    
    response = {
        "status": False,
        "message": e,
        "error_obj": {
            "error_code": "",
            "error_message": ""
        }
    }
    return JSONResponse(
        status_code=500,
        content=response
    )
