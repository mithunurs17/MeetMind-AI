"""
middleware.py — security and observability middleware stack.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("meetmind")


# ── 1. Security headers ───────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds sensible security headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store"
        # MutableHeaders uses __delitem__, NOT .pop()
        if "server" in response.headers:
            del response.headers["server"]
        if "x-powered-by" in response.headers:
            del response.headers["x-powered-by"]
        return response


# ── 2. In-memory sliding-window rate limiter ──────────────────────────────
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 200,
        window_secs: int = 60,
        burst_paths: list[str] | None = None,
        burst_max: int = 10,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_secs = window_secs
        self.burst_paths = burst_paths or ["/auth/login", "/auth/register"]
        self.burst_max = burst_max
        self._store: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = self._client_ip(request)
        now = time.time()
        window_start = now - self.window_secs

        self._store[ip] = [t for t in self._store[ip] if t > window_start]

        limit = self.burst_max if request.url.path in self.burst_paths else self.max_requests

        if len(self._store[ip]) >= limit:
            logger.warning("Rate limit exceeded for IP %s on %s", ip, request.url.path)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(self.window_secs)},
            )

        self._store[ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - len(self._store[ip]))
        return response


# ── 3. Request logging & correlation IDs ─────────────────────────────────
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = str(uuid.uuid4())[:8]
        request.state.request_id = req_id
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "[%s] %s %s -> %d  (%.1f ms)",
            req_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Request-ID"] = req_id
        return response