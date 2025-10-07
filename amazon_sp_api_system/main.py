"""
亚马逊SP API分析系统主程序
提供FastAPI Web服务和配置管理界面
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router, init_config_manager
from app.config.sp_api_config import MultiStoreConfig

# 创建FastAPI应用
app = FastAPI(
    title="亚马逊SP API分析系统",
    description="多店铺亚马逊卖家数据分析与监控平台",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化配置管理器
config_manager = MultiStoreConfig()
init_config_manager(config_manager)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 创建静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)


# 提供配置管理控制台页面
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回配置管理控制台首页"""
    html_file = os.path.join(static_dir, "config.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    else:
        return """
        <html>
        <head><title>亚马逊SP API配置管理</title></head>
        <body>
            <h1>配置管理页面加载中...</h1>
            <p>请稍候，正在初始化系统...</p>
        </body>
        </html>
        """


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "total_stores": len(config_manager.stores),
        "enabled_stores": len(config_manager.get_all_stores())
    }


# 挂载静态文件目录
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def main():
    """启动应用"""
    print("="*60)
    print("🚀 亚马逊SP API分析系统启动中...")
    print("="*60)
    print(f"📁 配置文件: {config_manager.config_file}")
    print(f"🏪 已加载店铺数量: {len(config_manager.stores)}")
    print("="*60)
    print("📡 访问地址:")
    print("   - 配置管理控制台: http://localhost:8000")
    print("   - API文档: http://localhost:8000/docs")
    print("   - API端点: http://localhost:8000/api")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()