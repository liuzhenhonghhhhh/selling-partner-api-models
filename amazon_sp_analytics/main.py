"""
主程序入口
集成SP API数据采集和数据库存储
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from datetime import datetime, timedelta
import threading
import time

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("亚马逊SP API多店铺销售分析系统")
    logger.info("=" * 60)
    
    # 读取配置
    config_file = os.getenv("SP_API_CONFIG", "config.yaml")
    
    if not os.path.exists(config_file):
        logger.warning(f"配置文件不存在: {config_file}")
        logger.info("请先创建配置文件:")
        logger.info("  cp config.yaml.example config.yaml")
        logger.info("  然后编辑 config.yaml 填入您的SP API凭证")
        return
    
    # 初始化数据库
    from app.models.database import DatabaseManager
    from app.services.data_storage import DataStorageService
    
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/sp_analytics?charset=utf8mb4"
    )
    
    logger.info(f"连接数据库...")
    try:
        db_manager = DatabaseManager(database_url)
        
        # 创建基础表
        db_manager.create_all_tables()
        logger.success("基础表创建成功")
        
        # 自动创建最近3个月的分表
        start_date = datetime.now().replace(day=1) - timedelta(days=90)
        end_date = datetime.now()
        db_manager.auto_create_tables_for_date_range(start_date, end_date)
        logger.success("月份分表创建成功")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        logger.info("请检查数据库连接配置")
        return
    
    # 初始化存储服务
    storage_service = DataStorageService(db_manager)
    
    # 启动数据采集
    try:
        from app.config import MultiStoreConfig, SPAPIConfig
        from app.core import MultiStoreClient
        from app.analytics import MultiStoreOrdersAnalytics, MultiStoreSalesAnalytics, MultiStoreFinanceAnalytics
        from app.utils import RealtimeMonitor
        
        # 加载配置
        multi_store_config = MultiStoreConfig(config_file)
        global_config = multi_store_config.global_config
        
        # 创建多店铺客户端
        multi_store_client = MultiStoreClient(global_config)
        
        # 添加所有店铺
        stores_count = 0
        for store in multi_store_config.get_all_stores():
            multi_store_client.add_store(store)
            
            # 保存店铺信息到数据库
            store_data = {
                'store_id': store.store_id,
                'store_name': store.store_name,
                'region': store.region.value,
                'marketplace_ids': store.marketplace_ids,
                'client_id': store.client_id,
                'client_secret': store.client_secret,
                'refresh_token': store.refresh_token,
                'enabled': store.enabled
            }
            storage_service.save_store(store_data)
            
            logger.info(f"已添加店铺: {store.store_name}")
            stores_count += 1
        
        logger.success(f"共加载 {stores_count} 个店铺")
        
        # 创建监控器
        monitor = RealtimeMonitor(
            multi_store_client=multi_store_client,
            update_interval=60  # 每分钟更新
        )
        
        # 设置告警
        monitor.set_alert_threshold("min_orders_per_hour", 10)
        monitor.set_alert_threshold("min_profit_margin", 5)
        
        # 添加告警回调 - 保存到数据库
        def save_alert_to_db(alerts):
            for alert in alerts:
                alert_data = {
                    'type': alert['type'],
                    'severity': alert['severity'],
                    'message': alert['message'],
                    'value': alert.get('value'),
                    'threshold': alert.get('threshold')
                }
                storage_service.save_alert(alert_data)
                logger.warning(f"[告警] {alert['message']}")
        
        monitor.add_alert_callback(save_alert_to_db)
        
        # 扩展监控器 - 保存数据到数据库
        original_collect = monitor._collect_metrics
        
        def collect_and_save():
            metrics = original_collect()
            if metrics:
                # 保存监控快照
                snapshot_data = {
                    'total_stores': metrics.get('orders', {}).get('total_stores', 0),
                    'total_orders_1h': metrics.get('orders', {}).get('total_orders', 0),
                    'total_revenue_1h': metrics.get('orders', {}).get('total_revenue', 0),
                    'total_revenue_24h': metrics.get('sales', {}).get('total_sales', 0),
                    'total_profit_7d': metrics.get('finance', {}).get('total_profit', 0),
                    'orders_per_hour': metrics.get('orders', {}).get('orders_per_hour', 0),
                    'revenue_per_hour': metrics.get('orders', {}).get('revenue_per_hour', 0),
                    'average_order_value': metrics.get('orders', {}).get('average_order_value', 0),
                    'average_profit_margin': metrics.get('finance', {}).get('average_profit_margin', 0),
                    'store_metrics': metrics.get('orders', {}).get('store_metrics', [])
                }
                storage_service.save_monitoring_snapshot(snapshot_data)
                
                logger.info(f"数据已保存 - 订单: {snapshot_data['total_orders_1h']}, "
                          f"收入: ${snapshot_data['total_revenue_1h']:.2f}")
            
            return metrics
        
        monitor._collect_metrics = collect_and_save
        
        # 启动监控
        monitor.start()
        logger.success("数据采集已启动 - 每60秒更新一次")
        
        # 保持运行
        logger.info("=" * 60)
        logger.info("系统正在运行中...")
        logger.info("按 Ctrl+C 停止")
        logger.info("=" * 60)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n正在停止系统...")
            monitor.stop()
            logger.info("系统已停止")
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 确保目录存在
    os.makedirs("logs", exist_ok=True)
    
    main()