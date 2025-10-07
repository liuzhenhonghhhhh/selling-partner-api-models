#!/bin/bash
# 启动脚本

echo "启动亚马逊SP API分析系统..."

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 启动服务
python3 main.py