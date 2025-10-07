"""
SP API Analytics 主程序
演示如何使用多店铺分析系统
"""
import sys
from datetime import datetime, timedelta
from loguru import logger

from config import MultiStoreConfig, SPAPIConfig, StoreCredentials, Region, MARKETPLACES
from core import MultiStoreClient
from analytics import MultiStoreOrdersAnalytics, MultiStoreSalesAnalytics, MultiStoreFinanceAnalytics
from cache import init_cache
from utils import RealtimeMonitor, DashboardData


# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/sp_api_analytics_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


class SPAPIAnalyticsPlatform:
    """SP API分析平台主类"""
    
    def __init__(self, config_file: str = "stores_config.yaml"):
        logger.info("初始化SP API分析平台...")
        
        # 加载配置
        self.multi_store_config = MultiStoreConfig(config_file)
        self.global_config = self.multi_store_config.global_config
        
        # 初始化缓存
        self.cache = init_cache(
            host=self.global_config.redis_host,
            port=self.global_config.redis_port,
            db=self.global_config.redis_db,
            password=self.global_config.redis_password
        )
        
        # 初始化多店铺客户端
        self.multi_store_client = MultiStoreClient(self.global_config)
        
        # 添加所有店铺
        for store in self.multi_store_config.get_all_stores():
            self.multi_store_client.add_store(store)
        
        # 获取所有客户端
        clients = self.multi_store_client.get_all_clients()
        
        # 初始化分析器
        self.orders_analytics = MultiStoreOrdersAnalytics(clients)
        self.sales_analytics = MultiStoreSalesAnalytics(clients)
        self.finance_analytics = MultiStoreFinanceAnalytics(clients)
        
        # 初始化实时监控
        self.monitor = RealtimeMonitor(
            multi_store_client=self.multi_store_client,
            update_interval=60  # 每分钟更新一次
        )
        
        # 仪表板数据
        self.dashboard = DashboardData(self.monitor)
        
        logger.success(f"平台初始化完成，已加载 {len(clients)} 个店铺")
    
    def show_realtime_metrics(self):
        """显示实时指标（最近1小时订单）"""
        logger.info("=" * 60)
        logger.info("实时指标 (最近1小时订单)")
        logger.info("=" * 60)
        
        metrics = self.orders_analytics.get_all_stores_metrics(time_window_minutes=60)
        
        logger.info(f"总店铺数: {metrics['total_stores']}")
        logger.info(f"总订单数: {metrics['total_orders']}")
        logger.info(f"总收入: ${metrics['total_revenue']:,.2f}")
        logger.info(f"平均订单价值: ${metrics['average_order_value']:,.2f}")
        logger.info(f"订单速率: {metrics['orders_per_hour']:.2f} 单/小时")
        logger.info(f"收入速率: ${metrics['revenue_per_hour']:,.2f}/小时")
        
        logger.info("\n各店铺表现:")
        for store in metrics['store_metrics'][:10]:  # 显示前10个店铺
            logger.info(
                f"  [{store['store_name']}] "
                f"订单: {store['total_orders']} | "
                f"收入: ${store['total_amount']:,.2f} | "
                f"AOV: ${store['average_order_value']:,.2f}"
            )
    
    def show_sales_dashboard(self, hours: int = 24):
        """显示销售仪表板"""
        logger.info("=" * 60)
        logger.info(f"销售仪表板 (最近{hours}小时)")
        logger.info("=" * 60)
        
        dashboard = self.sales_analytics.get_all_stores_sales_dashboard(hours=hours)
        
        logger.info(f"总店铺数: {dashboard['total_stores']}")
        logger.info(f"总订单数: {dashboard['total_orders']}")
        logger.info(f"总销售件数: {dashboard['total_units']}")
        logger.info(f"总销售额: ${dashboard['total_sales']:,.2f}")
        logger.info(f"平均订单价值: ${dashboard['average_order_value']:,.2f}")
        logger.info(f"平均件/单: {dashboard['average_units_per_order']:.2f}")
    
    def show_profit_analysis(self, days: int = 7):
        """显示利润分析"""
        logger.info("=" * 60)
        logger.info(f"利润分析 (最近{days}天)")
        logger.info("=" * 60)
        
        summary = self.finance_analytics.get_all_stores_profit_summary(days=days)
        
        logger.info(f"总店铺数: {summary['total_stores']}")
        logger.info(f"总收入: ${summary['total_revenue']:,.2f}")
        logger.info(f"总费用: ${summary['total_fees']:,.2f}")
        logger.info(f"总退款: ${summary['total_refunds']:,.2f}")
        logger.info(f"净利润: ${summary['total_profit']:,.2f}")
        logger.info(f"利润率: {summary['average_profit_margin']:.2f}%")
        
        logger.info("\n各店铺利润:")
        for store in summary['store_profits'][:10]:
            logger.info(
                f"  [{store['store_name']}] "
                f"利润: ${store['net_profit']:,.2f} | "
                f"利润率: {store['profit_margin']:.2f}%"
            )
    
    def show_top_stores(self, hours: int = 24, metric: str = "total_sales", top_n: int = 10):
        """显示表现最好的店铺"""
        logger.info("=" * 60)
        logger.info(f"表现最好的{top_n}个店铺 (按{metric}排序)")
        logger.info("=" * 60)
        
        top_stores = self.sales_analytics.get_top_performing_stores(
            hours=hours,
            metric=metric,
            top_n=top_n
        )
        
        for i, store in enumerate(top_stores, 1):
            logger.info(
                f"{i}. [{store['store_name']}] "
                f"销售额: ${store['total_sales']:,.2f} | "
                f"订单: {store['total_orders']} | "
                f"件数: {store['total_units']}"
            )
    
    def start_monitoring(self):
        """启动实时监控"""
        logger.info("启动实时监控...")
        
        # 设置告警阈值
        self.monitor.set_alert_threshold("min_orders_per_hour", 10)
        self.monitor.set_alert_threshold("min_profit_margin", 5)
        
        # 添加告警回调
        def alert_handler(alerts):
            logger.warning(f"收到 {len(alerts)} 个告警:")
            for alert in alerts:
                logger.warning(f"  [{alert['severity']}] {alert['message']}")
        
        self.monitor.add_alert_callback(alert_handler)
        
        # 启动监控
        self.monitor.start()
        
        logger.success("实时监控已启动")
    
    def show_overview_dashboard(self):
        """显示概览仪表板"""
        logger.info("=" * 60)
        logger.info("概览仪表板")
        logger.info("=" * 60)
        
        overview = self.dashboard.get_overview_dashboard()
        
        if "error" in overview:
            logger.warning(overview["error"])
            return
        
        logger.info(f"数据时间: {overview['timestamp']}")
        logger.info("\n总览:")
        ov = overview['overview']
        logger.info(f"  总店铺数: {ov['total_stores']}")
        logger.info(f"  订单速率: {ov['orders_per_hour']:.2f} 单/小时")
        logger.info(f"  收入速率: ${ov['revenue_per_hour']:,.2f}/小时")
        logger.info(f"  24小时销售额: ${ov['total_revenue_24h']:,.2f}")
        logger.info(f"  7天净利润: ${ov['total_profit_7d']:,.2f}")
        logger.info(f"  利润率: {ov['profit_margin']:.2f}%")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("亚马逊SP API多店铺销售分析系统")
    logger.info("=" * 60)
    
    # 创建示例配置（如果不存在）
    import os
    if not os.path.exists("stores_config.yaml"):
        from config.sp_api_config import create_sample_config
        create_sample_config("stores_config.yaml")
        logger.warning("请先配置 stores_config.yaml 文件，然后重新运行程序")
        return
    
    # 初始化平台
    platform = SPAPIAnalyticsPlatform()
    
    # 显示各项分析
    try:
        # 1. 实时指标（1小时）
        platform.show_realtime_metrics()
        
        # 2. 销售仪表板（24小时）
        platform.show_sales_dashboard(hours=24)
        
        # 3. 利润分析（7天）
        platform.show_profit_analysis(days=7)
        
        # 4. 排名前10的店铺
        platform.show_top_stores(hours=24, top_n=10)
        
        # 5. 启动实时监控
        # platform.start_monitoring()
        
        # 6. 显示概览仪表板
        # import time
        # time.sleep(70)  # 等待第一次数据采集
        # platform.show_overview_dashboard()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止监控
        if platform.monitor.is_running:
            platform.monitor.stop()


if __name__ == "__main__":
    main()