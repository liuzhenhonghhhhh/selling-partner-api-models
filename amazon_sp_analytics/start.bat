@echo off
echo ==================================================
echo   🚀 亚马逊SP API配置管理系统
echo ==================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
    echo ✅ 依赖安装完成
    echo.
)

echo 🌟 启动配置管理控制台...
echo.
echo 访问地址:
echo   - 配置管理界面: http://localhost:8000
echo   - API文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ==================================================
echo.

python main.py