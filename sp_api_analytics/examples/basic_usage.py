"""
基础用法示例
演示如何使用SP API分析系统的核心功能
"""
import sys
sys.path.insert(0, '..')

from datetime import datetime, timedelta
from config import StoreCredentials, SPAPIConfig, Region, MARKETPLACES
from core import SPAPIClient
from analytics import OrdersAnalytics, SalesAnalytics, FinanceAnalytics


def example_1_single_store_orders():
    """示例1: 单店铺订单分析"""
    print("=" * 60)
    print("示例1: 单店铺订单分析")
    print("=" * 60)
    
    # 创建店铺凭证
    credentials = StoreCredentials(
        store_id="my_store_001",
        store_name="我的美国店铺",
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        region=Region.NA,
        marketplace_ids=[MARKETPLACES["US"].marketplace_id]
    )
    
    # 创建客户端
    config = SPAPIConfig()
    client = SPAPIClient(credentials, config)
    
    # 创建订单分析器
    orders_analytics = OrdersAnalytics(client)
    
    # 获取最近24小时的订单
    recent_orders = orders_analytics.get_recent_orders(
        marketplace_ids=credentials.marketplace_ids,
        hours=24
    )
    
    print(f"获取到 {len(recent_orders)} 个订单")
    
    # 分析订单
    analysis = orders_analytics.analyze_orders(recent_orders)
    
    print(f"\n订单分析结果:")
    print(f"  总订单数: {analysis['total_orders']}")
    print(f"  总金额: ${analysis['total_amount']:,.2f}")
    print(f"  平均订单价值: ${analysis['average_order_value']:,.2f}")
    print(f"  按状态统计: {analysis['orders_by_status']}")
    print(f"  按渠道统计: {analysis['orders_by_channel']}")


def example_2_realtime_monitoring():
    """示例2: 实时订单监控（分钟级）"""
    print("\n" + "=" * 60)
    print("示例2: 实时订单监控")
    print("=" * 60)
    
    credentials = StoreCredentials(
        store_id="my_store_001",
        store_name="我的美国店铺",
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        region=Region.NA,
        marketplace_ids=[MARKETPLACES["US"].marketplace_id]
    )
    
    config = SPAPIConfig()
    client = SPAPIClient(credentials, config)
    orders_analytics = OrdersAnalytics(client)
    
    # 获取最近60分钟的实时指标
    realtime_metrics = orders_analytics.get_order_metrics_realtime(
        marketplace_ids=credentials.marketplace_ids,
        time_window_minutes=60
    )
    
    print(f"\n实时指标 (最近60分钟):")
    print(f"  订单数: {realtime_metrics['total_orders']}")
    print(f"  收入: ${realtime_metrics['total_amount']:,.2f}")
    print(f"  订单速率: {realtime_metrics['orders_per_hour']:.2f} 单/小时")
    print(f"  收入速率: ${realtime_metrics['revenue_per_hour']:,.2f}/小时")


def example_3_sales_analysis():
    """示例3: 销售数据分析"""
    print("\n" + "=" * 60)
    print("示例3: 销售数据分析")
    print("=" * 60)
    
    credentials = StoreCredentials(
        store_id="my_store_001",
        store_name="我的美国店铺",
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        region=Region.NA,
        marketplace_ids=[MARKETPLACES["US"].marketplace_id]
    )
    
    config = SPAPIConfig()
    client = SPAPIClient(credentials, config)
    sales_analytics = SalesAnalytics(client)
    
    # 获取最近24小时的销售仪表板
    dashboard = sales_analytics.get_realtime_sales_dashboard(
        marketplace_ids=credentials.marketplace_ids,
        hours=24
    )
    
    print(f"\n销售仪表板 (24小时):")
    print(f"  订单数: {dashboard['total_orders']}")
    print(f"  销售件数: {dashboard['total_units']}")
    print(f"  销售额: ${dashboard['total_sales']:,.2f}")
    print(f"  平均订单价值: ${dashboard['average_order_value']:,.2f}")
    print(f"  平均件/单: {dashboard['average_units_per_order']:.2f}")
    
    # 计算增长率
    growth = sales_analytics.calculate_growth_rate(
        marketplace_ids=credentials.marketplace_ids,
        current_days=7,
        comparison_days=7
    )
    
    print(f"\n增长率分析 (对比上周):")
    print(f"  订单增长: {growth['growth_rates']['orders_growth']:+.2f}%")
    print(f"  销售额增长: {growth['growth_rates']['sales_growth']:+.2f}%")
    print(f"  件数增长: {growth['growth_rates']['units_growth']:+.2f}%")


def example_4_profit_analysis():
    """示例4: 利润分析"""
    print("\n" + "=" * 60)
    print("示例4: 利润分析")
    print("=" * 60)
    
    credentials = StoreCredentials(
        store_id="my_store_001",
        store_name="我的美国店铺",
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        region=Region.NA,
        marketplace_ids=[MARKETPLACES["US"].marketplace_id]
    )
    
    config = SPAPIConfig()
    client = SPAPIClient(credentials, config)
    finance_analytics = FinanceAnalytics(client)
    
    # 获取最近7天的利润分析
    profit = finance_analytics.get_profit_analysis(days=7)
    
    print(f"\n利润分析 (7天):")
    print(f"  收入: ${profit['revenue']:,.2f}")
    print(f"  费用: ${profit['fees']:,.2f}")
    print(f"  退款: ${profit['refunds']:,.2f}")
    print(f"  净利润: ${profit['net_profit']:,.2f}")
    print(f"  利润率: {profit['profit_margin']:.2f}%")
    
    print(f"\n收入明细:")
    for charge_type, amount in profit['revenue_breakdown'].items():
        print(f"  {charge_type}: ${amount:,.2f}")
    
    print(f"\n费用明细:")
    for fee_type, amount in profit['fee_breakdown'].items():
        print(f"  {fee_type}: ${amount:,.2f}")


def example_5_period_comparison():
    """示例5: 周期对比分析"""
    print("\n" + "=" * 60)
    print("示例5: 周期对比分析")
    print("=" * 60)
    
    credentials = StoreCredentials(
        store_id="my_store_001",
        store_name="我的美国店铺",
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        region=Region.NA,
        marketplace_ids=[MARKETPLACES["US"].marketplace_id]
    )
    
    config = SPAPIConfig()
    client = SPAPIClient(credentials, config)
    
    # 订单对比
    orders_analytics = OrdersAnalytics(client)
    order_comparison = orders_analytics.compare_with_previous_period(
        marketplace_ids=credentials.marketplace_ids,
        current_hours=24
    )
    
    print(f"\n订单对比 (本周期 vs 上周期):")
    print(f"  订单变化: {order_comparison['changes']['orders_change_percent']:+.2f}%")
    print(f"  收入变化: {order_comparison['changes']['revenue_change_percent']:+.2f}%")
    print(f"  AOV变化: {order_comparison['changes']['aov_change_percent']:+.2f}%")
    
    # 利润对比
    finance_analytics = FinanceAnalytics(client)
    profit_comparison = finance_analytics.compare_profit_periods(
        current_days=7,
        comparison_days=7
    )
    
    print(f"\n利润对比 (本周 vs 上周):")
    print(f"  收入变化: {profit_comparison['changes']['revenue_change']:+.2f}%")
    print(f"  利润变化: {profit_comparison['changes']['profit_change']:+.2f}%")
    print(f"  费用变化: {profit_comparison['changes']['fee_change']:+.2f}%")


if __name__ == "__main__":
    print("SP API 分析系统 - 基础用法示例\n")
    
    # 运行示例（需要配置真实的API凭证）
    print("注意: 运行这些示例需要配置真实的SP API凭证")
    print("请在代码中替换 your_client_id, your_client_secret, your_refresh_token\n")
    
    # 取消注释以运行示例:
    # example_1_single_store_orders()
    # example_2_realtime_monitoring()
    # example_3_sales_analysis()
    # example_4_profit_analysis()
    # example_5_period_comparison()
    
    print("\n所有示例代码已准备就绪，请配置API凭证后运行！")