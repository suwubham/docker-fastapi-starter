from fastapi import FastAPI
from app.routers.user_router import user_router
from app.routers.redis_simple import router as redis_router

app = FastAPI()

app.include_router(user_router, prefix='/api')
app.include_router(redis_router, prefix='/api')

@app.get("/", tags=['Root'])
def read_root():
    return {"message": "Docker FastAPI Starter!"}



