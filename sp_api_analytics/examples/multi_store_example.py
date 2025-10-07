"""
多店铺分析示例
演示如何管理和分析100+店铺的数据
"""
import sys
sys.path.insert(0, '..')

import time
from datetime import datetime
from config import MultiStoreConfig, SPAPIConfig, StoreCredentials, Region, MARKETPLACES
from core import MultiStoreClient
from analytics import MultiStoreOrdersAnalytics, MultiStoreSalesAnalytics, MultiStoreFinanceAnalytics
from utils import RealtimeMonitor, DashboardData


def example_1_batch_add_stores():
    """示例1: 批量添加店铺"""
    print("=" * 60)
    print("示例1: 批量添加100个店铺")
    print("=" * 60)
    
    config = SPAPIConfig()
    multi_store_client = MultiStoreClient(config)
    
    # 批量添加店铺（示例：假设有100个店铺）
    stores = []
    for i in range(1, 101):
        store = StoreCredentials(
            store_id=f"store_{i:03d}",
            store_name=f"店铺{i:03d}",
            client_id=f"client_id_{i}",
            client_secret=f"client_secret_{i}",
            refresh_token=f"refresh_token_{i}",
            region=Region.NA if i % 3 == 0 else (Region.EU if i % 3 == 1 else Region.FE),
            marketplace_ids=[MARKETPLACES["US"].marketplace_id],
            enabled=True
        )
        stores.append(store)
        multi_store_client.add_store(store)
    
    print(f"已添加 {len(stores)} 个店铺")
    
    # 按区域统计
    na_stores = [s for s in stores if s.region == Region.NA]
    eu_stores = [s for s in stores if s.region == Region.EU]
    fe_stores = [s for s in stores if s.region == Region.FE]
    
    print(f"  北美区: {len(na_stores)} 个店铺")
    print(f"  欧洲区: {len(eu_stores)} 个店铺")
    print(f"  远东区: {len(fe_stores)} 个店铺")


def example_2_aggregate_all_stores():
    """示例2: 聚合所有店铺数据"""
    print("\n" + "=" * 60)
    print("示例2: 聚合所有店铺的实时数据")
    print("=" * 60)
    
    # 使用配置文件加载店铺
    multi_store_config = MultiStoreConfig("stores_config.yaml")
    global_config = multi_store_config.global_config
    
    # 创建多店铺客户端
    multi_store_client = MultiStoreClient(global_config)
    
    # 添加所有店铺
    for store in multi_store_config.get_all_stores():
        multi_store_client.add_store(store)
    
    # 获取所有客户端
    clients = multi_store_client.get_all_clients()
    
    # 创建聚合分析器
    orders_analytics = MultiStoreOrdersAnalytics(clients)
    
    # 获取所有店铺的实时指标
    print("\n正在采集所有店铺数据...")
    all_metrics = orders_analytics.get_all_stores_metrics(time_window_minutes=60)
    
    print(f"\n聚合结果 (最近60分钟):")
    print(f"  总店铺数: {all_metrics['total_stores']}")
    print(f"  总订单数: {all_metrics['total_orders']}")
    print(f"  总收入: ${all_metrics['total_revenue']:,.2f}")
    print(f"  平均AOV: ${all_metrics['average_order_value']:,.2f}")
    print(f"  订单速率: {all_metrics['orders_per_hour']:.2f} 单/小时")
    print(f"  收入速率: ${all_metrics['revenue_per_hour']:,.2f}/小时")


def example_3_top_performing_stores():
    """示例3: 找出表现最好的店铺"""
    print("\n" + "=" * 60)
    print("示例3: 排名前20的店铺")
    print("=" * 60)
    
    multi_store_config = MultiStoreConfig("stores_config.yaml")
    global_config = multi_store_config.global_config
    
    multi_store_client = MultiStoreClient(global_config)
    for store in multi_store_config.get_all_stores():
        multi_store_client.add_store(store)
    
    clients = multi_store_client.get_all_clients()
    sales_analytics = MultiStoreSalesAnalytics(clients)
    
    # 按销售额排名
    print("\n按销售额排名:")
    top_by_sales = sales_analytics.get_top_performing_stores(
        hours=24,
        metric='total_sales',
        top_n=20
    )
    
    for i, store in enumerate(top_by_sales, 1):
        print(
            f"  {i:2d}. [{store['store_name']}] "
            f"销售额: ${store['total_sales']:>10,.2f} | "
            f"订单: {store['total_orders']:>5d} | "
            f"件数: {store['total_units']:>5d}"
        )
    
    # 按订单量排名
    print("\n按订单量排名:")
    top_by_orders = sales_analytics.get_top_performing_stores(
        hours=24,
        metric='total_orders',
        top_n=20
    )
    
    for i, store in enumerate(top_by_orders, 1):
        print(
            f"  {i:2d}. [{store['store_name']}] "
            f"订单: {store['total_orders']:>5d} | "
            f"销售额: ${store['total_sales']:>10,.2f}"
        )


def example_4_realtime_monitoring():
    """示例4: 实时监控所有店铺"""
    print("\n" + "=" * 60)
    print("示例4: 启动实时监控系统")
    print("=" * 60)
    
    multi_store_config = MultiStoreConfig("stores_config.yaml")
    global_config = multi_store_config.global_config
    
    multi_store_client = MultiStoreClient(global_config)
    for store in multi_store_config.get_all_stores():
        multi_store_client.add_store(store)
    
    # 创建监控器
    monitor = RealtimeMonitor(
        multi_store_client=multi_store_client,
        update_interval=60  # 每分钟更新一次
    )
    
    # 设置告警阈值
    monitor.set_alert_threshold("min_orders_per_hour", 100)  # 100个店铺，每小时至少100单
    monitor.set_alert_threshold("min_profit_margin", 10)    # 利润率不低于10%
    
    # 添加告警处理
    def alert_handler(alerts):
        print(f"\n{'='*60}")
        print(f"⚠️  收到 {len(alerts)} 个告警 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        print(f"{'='*60}")
        for alert in alerts:
            severity = "🔴" if alert['severity'] == 'critical' else "🟡"
            print(f"{severity} [{alert['type']}] {alert['message']}")
    
    monitor.add_alert_callback(alert_handler)
    
    # 启动监控
    print("\n启动监控...")
    monitor.start()
    
    # 创建仪表板
    dashboard = DashboardData(monitor)
    
    # 模拟运行5分钟
    print("监控运行中... (按Ctrl+C停止)")
    try:
        for i in range(5):
            time.sleep(60)
            
            # 获取最新指标
            summary = monitor.get_metrics_summary()
            
            print(f"\n{'='*60}")
            print(f"实时监控状态 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"{'='*60}")
            print(f"状态: {summary['status']}")
            print(f"最后更新: {summary['last_update']}")
            print(f"总店铺数: {summary['total_stores']}")
            print(f"1小时订单数: {summary['total_orders_1h']}")
            print(f"24小时销售额: ${summary['total_revenue_24h']:,.2f}")
            print(f"7天利润: ${summary['total_profit_7d']:,.2f}")
            print(f"订单速率: {summary['orders_per_hour']:.2f} 单/小时")
            print(f"利润率: {summary['average_profit_margin']:.2f}%")
            
            # 获取店铺排名
            rankings = dashboard.get_store_rankings()
            if 'error' not in rankings:
                print(f"\n前5名店铺 (按订单量):")
                for j, store in enumerate(rankings['by_orders'][:5], 1):
                    print(f"  {j}. {store['store_name']}: {store['orders']} 单")
    
    except KeyboardInterrupt:
        print("\n\n用户中断监控")
    finally:
        monitor.stop()
        print("监控已停止")


def example_5_profit_summary():
    """示例5: 所有店铺利润汇总"""
    print("\n" + "=" * 60)
    print("示例5: 所有店铺利润汇总分析")
    print("=" * 60)
    
    multi_store_config = MultiStoreConfig("stores_config.yaml")
    global_config = multi_store_config.global_config
    
    multi_store_client = MultiStoreClient(global_config)
    for store in multi_store_config.get_all_stores():
        multi_store_client.add_store(store)
    
    clients = multi_store_client.get_all_clients()
    finance_analytics = MultiStoreFinanceAnalytics(clients)
    
    # 获取7天利润汇总
    print("\n正在分析所有店铺的利润数据...")
    profit_summary = finance_analytics.get_all_stores_profit_summary(days=7)
    
    print(f"\n利润汇总 (最近7天):")
    print(f"  总店铺数: {profit_summary['total_stores']}")
    print(f"  总收入: ${profit_summary['total_revenue']:,.2f}")
    print(f"  总费用: ${profit_summary['total_fees']:,.2f}")
    print(f"  总退款: ${profit_summary['total_refunds']:,.2f}")
    print(f"  净利润: ${profit_summary['total_profit']:,.2f}")
    print(f"  平均利润率: {profit_summary['average_profit_margin']:.2f}%")
    
    # 找出利润最高的店铺
    store_profits = sorted(
        profit_summary['store_profits'],
        key=lambda x: x['net_profit'],
        reverse=True
    )
    
    print(f"\n利润最高的10个店铺:")
    for i, store in enumerate(store_profits[:10], 1):
        print(
            f"  {i:2d}. [{store['store_name']}] "
            f"利润: ${store['net_profit']:>10,.2f} | "
            f"利润率: {store['profit_margin']:>6.2f}% | "
            f"收入: ${store['revenue']:>10,.2f}"
        )
    
    # 找出利润率最高的店铺
    store_margins = sorted(
        profit_summary['store_profits'],
        key=lambda x: x['profit_margin'],
        reverse=True
    )
    
    print(f"\n利润率最高的10个店铺:")
    for i, store in enumerate(store_margins[:10], 1):
        print(
            f"  {i:2d}. [{store['store_name']}] "
            f"利润率: {store['profit_margin']:>6.2f}% | "
            f"利润: ${store['net_profit']:>10,.2f} | "
            f"收入: ${store['revenue']:>10,.2f}"
        )


def example_6_performance_optimization():
    """示例6: 性能优化技巧"""
    print("\n" + "=" * 60)
    print("示例6: 性能优化技巧（针对100+店铺）")
    print("=" * 60)
    
    print("\n优化建议:")
    print("1. 使用Redis缓存减少API调用")
    print("2. 合理设置数据更新间隔（建议60秒）")
    print("3. 使用较短的时间窗口（如60分钟）")
    print("4. 启用并发采集（多线程/异步）")
    print("5. 只采集必要的数据字段")
    
    print("\n示例代码:")
    print("""
# 优化配置
config = SPAPIConfig()
config.cache_ttl['orders'] = 60  # 订单缓存60秒
config.cache_ttl['sales_metrics'] = 300  # 销售指标缓存5分钟

# 启用Redis缓存
from cache import init_cache
cache = init_cache(host='localhost', port=6379)

# 分批处理店铺
batch_size = 20
stores = multi_store_config.get_all_stores()

for i in range(0, len(stores), batch_size):
    batch = stores[i:i+batch_size]
    # 处理这批店铺...
    print(f"处理第 {i//batch_size + 1} 批店铺 ({len(batch)} 个)")

# 使用较短的时间窗口
metrics = orders_analytics.get_all_stores_metrics(
    time_window_minutes=60  # 只获取最近60分钟数据
)
    """)


if __name__ == "__main__":
    print("SP API 多店铺分析系统 - 高级示例\n")
    print("这些示例演示了如何管理和分析100+店铺的数据\n")
    
    # 运行示例（需要配置真实的API凭证）
    print("注意: 运行这些示例需要配置真实的SP API凭证")
    print("请先配置 stores_config.yaml 文件\n")
    
    # 取消注释以运行示例:
    # example_1_batch_add_stores()
    # example_2_aggregate_all_stores()
    # example_3_top_performing_stores()
    # example_4_realtime_monitoring()
    # example_5_profit_summary()
    # example_6_performance_optimization()
    
    print("\n所有示例代码已准备就绪！")