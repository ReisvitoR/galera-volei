"""
Middlewares de segurança para proteger a API contra ataques
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import re
from typing import Dict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Armazenar tentativas de requisições por IP (em produção, usar Redis)
request_counts: Dict[str, list] = defaultdict(list)

# Padrões de SQL Injection comuns
SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bselect\b.*\bfrom\b)",
    r"(\binsert\b.*\binto\b)",
    r"(\bupdate\b.*\bset\b)",
    r"(\bdelete\b.*\bfrom\b)",
    r"(\bdrop\b.*\btable\b)",
    r"(--\s*$)",
    r"(;\s*--)",
    r"(\bor\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
    r"(\band\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
    r"('.*\bor\b.*')",
    r"(\bexec\b|\bexecute\b)",
    r"(xp_cmdshell)",
]

# Padrões de XSS comuns
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*=",
    r"<iframe",
    r"<object",
    r"<embed",
]

# Padrões de Path Traversal
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"%2e%2e",
]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para limitar taxa de requisições (Rate Limiting)"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def dispatch(self, request: Request, call_next):
        # Pegar IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Endpoints excluídos do rate limiting
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Limpar requisições antigas
        current_time = time.time()
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # Verificar limite
        if len(request_counts[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Muitas requisições. Tente novamente mais tarde.",
                    "retry_after": self.window_seconds
                }
            )
        
        # Registrar requisição
        request_counts[client_ip].append(current_time)
        
        return await call_next(request)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware para validar inputs e prevenir ataques"""
    
    async def dispatch(self, request: Request, call_next):
        # Verificar apenas requisições com corpo (POST, PUT, PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Ler corpo da requisição
                body = await request.body()
                body_str = body.decode('utf-8').lower()
                
                # Verificar SQL Injection
                for pattern in SQL_INJECTION_PATTERNS:
                    if re.search(pattern, body_str, re.IGNORECASE):
                        logger.warning(f"SQL Injection attempt detected from {request.client.host}: {pattern}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Input inválido detectado"
                        )
                
                # Verificar XSS
                for pattern in XSS_PATTERNS:
                    if re.search(pattern, body_str, re.IGNORECASE):
                        logger.warning(f"XSS attempt detected from {request.client.host}: {pattern}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Input inválido detectado"
                        )
                
                # Recriar request com o corpo original
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
                
            except UnicodeDecodeError:
                # Corpo não é texto válido
                pass
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                # Outros erros, continuar normalmente
                logger.error(f"Error in input validation: {e}")
        
        # Verificar Path Traversal na URL
        path = request.url.path.lower()
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, path):
                logger.warning(f"Path traversal attempt detected from {request.client.host}: {path}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Caminho inválido"
                )
        
        return await call_next(request)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para limitar tamanho de requisições"""
    
    def __init__(self, app, max_size_mb: float = 10):
        super().__init__(app)
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    async def dispatch(self, request: Request, call_next):
        # Verificar Content-Length header
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size_bytes:
                logger.warning(f"Request too large from {request.client.host}: {content_length} bytes")
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Requisição muito grande"}
                )
        
        return await call_next(request)
