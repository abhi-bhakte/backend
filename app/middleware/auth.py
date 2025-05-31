from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import List, Callable
from app.utils.auth import verify_token  # Your verify function

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_paths: List[str] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or []

    async def dispatch(self, request: Request, call_next: Callable):
        # Allow all OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        path = request.url.path
        if path in self.exempt_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: Missing or invalid token"},
            )

        token = auth_header.split(" ")[1]
        try:
            verify_token(token)
        except Exception:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: Token verification failed"},
            )

        return await call_next(request)
