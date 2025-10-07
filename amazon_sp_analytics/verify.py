#!/usr/bin/env python3
"""
系统验证脚本
检查所有组件是否正常工作
"""

import sys
import os

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_imports():
    """检查必要的导入"""
    print_header("📦 检查依赖包")
    
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'yaml': 'PyYAML'
    }
    
    all_ok = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name:15} - 已安装")
        except ImportError:
            print(f"❌ {name:15} - 未安装")
            all_ok = False
    
    return all_ok

def check_files():
    """检查必要的文件"""
    print_header("📁 检查文件结构")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'static/config.html',
        'app/api/routes.py',
        'app/api/schemas.py',
        'app/config/sp_api_config.py',
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 不存在")
            all_ok = False
    
    return all_ok

def check_app():
    """检查应用是否可以导入"""
    print_header("🚀 检查应用")
    
    try:
        from main import app
        print("✅ FastAPI应用 - 导入成功")
        print(f"✅ 路由数量: {len(app.routes)}")
        return True
    except Exception as e:
        print(f"❌ FastAPI应用 - 导入失败: {e}")
        return False

def check_config():
    """检查配置管理器"""
    print_header("⚙️  检查配置管理器")
    
    try:
        from app.config.sp_api_config import MultiStoreConfig
        config = MultiStoreConfig()
        print("✅ 配置管理器 - 初始化成功")
        print(f"✅ 已加载店铺数: {len(config.stores)}")
        print(f"✅ 配置文件: {config.config_file}")
        return True
    except Exception as e:
        print(f"❌ 配置管理器 - 初始化失败: {e}")
        return False

def check_api_routes():
    """检查API路由"""
    print_header("🛣️  检查API路由")
    
    try:
        from app.api.routes import api_router
        routes = [route for route in api_router.routes]
        
        # 检查配置管理路由
        config_routes = [
            '/config/stores',
            '/config/test',
        ]
        
        found_routes = []
        for route in routes:
            if hasattr(route, 'path'):
                found_routes.append(route.path)
        
        for expected_route in config_routes:
            if any(expected_route in r for r in found_routes):
                print(f"✅ {expected_route}")
            else:
                print(f"⚠️  {expected_route} - 未找到")
        
        print(f"✅ API路由总数: {len(routes)}")
        return True
    except Exception as e:
        print(f"❌ API路由检查失败: {e}")
        return False

def main():
    """主函数"""
    print_header("🔍 亚马逊SP API配置管理系统 - 系统验证")
    
    results = []
    
    # 运行所有检查
    results.append(("依赖包", check_imports()))
    results.append(("文件结构", check_files()))
    results.append(("应用导入", check_app()))
    results.append(("配置管理器", check_config()))
    results.append(("API路由", check_api_routes()))
    
    # 打印总结
    print_header("📊 验证结果")
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status:8} - {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ 所有检查通过！系统可以正常使用。")
        print("\n启动方法:")
        print("  Linux/Mac: ./start.sh")
        print("  Windows:   start.bat")
        print("  手动:      python3 main.py")
        print("\n访问地址: http://localhost:8000")
        return 0
    else:
        print("❌ 部分检查失败，请修复后再试。")
        print("\n安装依赖:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())