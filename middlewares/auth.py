import traceback
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            if (
                '/auth/' not in request.url.path
                and '/health' not in request.url.path
                and '/openapi.json' not in request.url.path
                and '/docs' not in request.url.path
                and '/prompting' not in request.url.path
                and not 'user' in request.session
            ):
                return JSONResponse(
                    {'message': 'Request is not authenticated'}, status_code=401
                )
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # If token validation fails due to HTTPException, return the error response
            return JSONResponse(
                content={"detail": traceback.format_exc()}, status_code=exc.status_code
            )
        except:  # pylint: disable=bare-except
            # If token validation fails due to other exceptions, return a generic error response
            return JSONResponse(
                content={"detail": traceback.format_exc()}, status_code=500
            )
