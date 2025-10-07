"""
数据库初始化脚本
创建所有必要的表
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import DatabaseManager
from loguru import logger


def init_database():
    """初始化数据库"""
    # 读取数据库URL
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/sp_analytics?charset=utf8mb4"
    )
    
    logger.info(f"连接数据库: {database_url.split('@')[1]}")
    
    # 创建数据库管理器
    db_manager = DatabaseManager(database_url)
    
    # 创建基础表
    logger.info("创建基础表...")
    db_manager.create_all_tables()
    logger.success("基础表创建成功")
    
    # 创建最近12个月的分表
    logger.info("创建月份分表...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    db_manager.auto_create_tables_for_date_range(start_date, end_date)
    logger.success("月份分表创建成功")
    
    logger.success("数据库初始化完成！")


if __name__ == "__main__":
    init_database()