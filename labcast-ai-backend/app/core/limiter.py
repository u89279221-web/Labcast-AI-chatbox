import contextvars
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
request_var = contextvars.ContextVar("request_var", default=None)
