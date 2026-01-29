from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.routes import api_router
from app.websocket import router as websocket_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    # 初始化数据库
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down...")
    # 关闭数据库连接、Redis 等


app = FastAPI(
    title="评教系统后端 API",
    description="广西警察学院评教系统后端接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")
# 注册WebSocket路由
app.include_router(websocket_router)


@app.get("/")
def read_root():
    return {"message": "评教系统后端 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
