from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.redis import get_redis

router = APIRouter(prefix="/redis", tags=["Redis"])

class KeyValue(BaseModel):
    key: str
    value: str

class GetResponse(BaseModel):
    key: str
    value: str

@router.post("/put")
async def put_value(item: KeyValue):
    """Put a key-value pair in Redis"""
    try:
        redis_client = get_redis()
        redis_client.set(item.key, item.value)
        return {"message": f"Successfully stored key: {item.key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store value: {str(e)}")

@router.get("/get/{key}", response_model=GetResponse)
async def get_value(key: str):
    """Get a value from Redis by key"""
    try:
        redis_client = get_redis()
        value = redis_client.get(key)
        
        if value is None:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        
        return GetResponse(key=key, value=value)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve value: {str(e)}")

@router.delete("/delete/{key}")
async def delete_value(key: str):
    """Delete a key from Redis"""
    try:
        redis_client = get_redis()
        deleted = redis_client.delete(key)
        
        if deleted:
            return {"message": f"Successfully deleted key: {key}"}
        else:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete key: {str(e)}")

@router.get("/ping")
async def ping_redis():
    """Check if Redis is connected"""
    try:
        redis_client = get_redis()
        redis_client.ping()
        return {"message": "Redis is connected!"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis connection failed: {str(e)}")
