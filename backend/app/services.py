import asyncio, logging
from pathlib import Path
from fastapi import UploadFile
from redis import Redis
from .core.config import settings
log=logging.getLogger(__name__)
def redis_client() -> Redis | None:
    try: return Redis.from_url(settings.redis_url,decode_responses=True,socket_connect_timeout=.2)
    except Exception: return None
def rate_limit(key:str, limit:int, seconds:int) -> None:
    r=redis_client()
    if not r: return
    try:
        count=r.incr(key)
        if count==1:r.expire(key,seconds)
        if count>limit: from fastapi import HTTPException; raise HTTPException(429,detail={"code":"rate_limited","message":"Please try again later."})
    except ConnectionError: pass
class StorageService:
    async def save(self,file:UploadFile)->str:
        if settings.storage_provider!="local": raise RuntimeError("Cloud storage provider is not configured")
        target=Path("uploads"); target.mkdir(exist_ok=True); name=f"{file.filename}".replace("/","").replace("\\","")
        (target/name).write_bytes(await file.read()); return f"/uploads/{name}"
def notify(kind:str) -> None:
    if not settings.smtp_host: log.info("%s stored; SMTP notification is not configured",kind); return
    log.info("%s notification delivery should be handled by configured SMTP worker",kind)
