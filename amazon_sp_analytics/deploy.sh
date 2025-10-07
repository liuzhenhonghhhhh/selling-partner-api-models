#!/bin/bash
# 部署脚本

echo "================================"
echo "亚马逊SP API分析系统 - 部署脚本"
echo "================================"

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "创建目录..."
mkdir -p logs
mkdir -p data
mkdir -p static/css
mkdir -p static/js
mkdir -p templates

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "创建配置文件..."
    cp config.yaml.example config.yaml
    echo "请编辑 config.yaml 填入您的SP API凭证"
fi

if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请编辑 .env 填入数据库配置"
fi

# 初始化数据库
echo "初始化数据库..."
python3 scripts/init_database.py

echo "================================"
echo "部署完成！"
echo "================================"
echo ""
echo "下一步操作："
echo "1. 编辑 config.yaml 填入您的SP API凭证"
echo "2. 编辑 .env 填入数据库配置"
echo "3. 运行: ./start.sh"
echo ""