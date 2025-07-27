from starlette.middleware.base import BaseHTTPMiddleware

class FastAPISafeguardMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config, **kwargs):
        super().__init__(app, **kwargs)
        self.config = config
