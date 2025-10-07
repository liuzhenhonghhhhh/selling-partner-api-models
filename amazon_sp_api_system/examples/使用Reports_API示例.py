"""
使用Reports API获取销售和库存数据的完整示例
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime

from app.config.sp_api_config import MultiStoreConfig
from app.models.mysql_manager import create_mysql_manager_from_config
from app.services.report_service import ReportProcessingService
from app.services.report_scheduler import ReportScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_manual_sales_report():
    """示例1: 手动获取销售报告"""
    print("\n" + "="*60)
    print("示例1: 手动获取销售报告")
    print("="*60)
    
    # 1. MySQL配置
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'amazon_user',
        'password': '你的密码',  # 请修改为实际密码
        'database': 'amazon_sp',
        'charset': 'utf8mb4',
        'auto_create_tables': True
    }
    
    # 2. 初始化
    print("初始化配置和数据库管理器...")
    config_manager = MultiStoreConfig()
    db_manager = create_mysql_manager_from_config(mysql_config)
    service = ReportProcessingService(db_manager)
    
    # 3. 获取店铺列表
    stores = config_manager.get_all_stores()
    print(f"找到 {len(stores)} 个启用的店铺")
    
    # 4. 处理销售报告
    print("\n开始获取最近7天的销售报告...")
    results = service.process_all_stores_sales(stores, days_ago=7)
    
    # 5. 显示结果
    print("\n处理结果:")
    for result in results:
        if result['success']:
            print(f"  ✅ {result['store_name']}")
            print(f"     - 按日期记录: {result['records_by_date']} 条")
            print(f"     - 按ASIN记录: {result['records_by_asin']} 条")
            print(f"     - 报告ID: {result['report_id']}")
        else:
            print(f"  ❌ {result['store_name']}: {result.get('error', '未知错误')}")
    
    print("\n✅ 销售报告获取完成！数据已保存到MySQL数据库")


def example_2_manual_inventory_report():
    """示例2: 手动获取库存报告"""
    print("\n" + "="*60)
    print("示例2: 手动获取库存报告")
    print("="*60)
    
    # MySQL配置
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'amazon_user',
        'password': '你的密码',  # 请修改为实际密码
        'database': 'amazon_sp'
    }
    
    # 初始化
    config_manager = MultiStoreConfig()
    db_manager = create_mysql_manager_from_config(mysql_config)
    service = ReportProcessingService(db_manager)
    
    # 获取店铺
    stores = config_manager.get_all_stores()
    
    # 处理库存报告
    print("\n开始获取最近7天的库存报告...")
    results = service.process_all_stores_inventory(stores, days_ago=7)
    
    # 显示结果
    print("\n处理结果:")
    for result in results:
        if result['success']:
            print(f"  ✅ {result['store_name']}")
            print(f"     - 汇总记录: {result['records_aggregate']} 条")
            print(f"     - ASIN记录: {result['records_by_asin']} 条")
        else:
            print(f"  ❌ {result['store_name']}: {result.get('error', '未知错误')}")


def example_3_single_store_report():
    """示例3: 获取单个店铺的报告"""
    print("\n" + "="*60)
    print("示例3: 获取单个店铺的报告")
    print("="*60)
    
    # MySQL配置
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'amazon_user',
        'password': '你的密码',
        'database': 'amazon_sp'
    }
    
    # 初始化
    config_manager = MultiStoreConfig()
    db_manager = create_mysql_manager_from_config(mysql_config)
    service = ReportProcessingService(db_manager)
    
    # 获取单个店铺
    store_id = "store_001"  # 修改为实际店铺ID
    store_credentials = config_manager.get_store(store_id)
    
    if not store_credentials:
        print(f"❌ 未找到店铺: {store_id}")
        return
    
    print(f"\n处理店铺: {store_credentials.store_name}")
    
    # 获取销售报告
    print("\n1. 获取销售报告...")
    sales_result = service.process_sales_report(
        store_credentials,
        days_ago=7,
        date_granularity="DAY",
        asin_granularity="SKU"
    )
    
    if sales_result['success']:
        print(f"   ✅ 成功: {sales_result['records_by_date']} 条日期记录")
    else:
        print(f"   ❌ 失败: {sales_result.get('error')}")
    
    # 获取库存报告
    print("\n2. 获取库存报告...")
    inventory_result = service.process_inventory_report(
        store_credentials,
        days_ago=7,
        report_period="DAY"
    )
    
    if inventory_result['success']:
        print(f"   ✅ 成功: {inventory_result['records_aggregate']} 条汇总记录")
    else:
        print(f"   ❌ 失败: {inventory_result.get('error')}")


def example_4_scheduled_reports():
    """示例4: 使用定时调度器"""
    print("\n" + "="*60)
    print("示例4: 使用定时调度器自动获取报告")
    print("="*60)
    
    # MySQL配置
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'amazon_user',
        'password': '你的密码',
        'database': 'amazon_sp'
    }
    
    # 初始化
    config_manager = MultiStoreConfig()
    db_manager = create_mysql_manager_from_config(mysql_config)
    scheduler = ReportScheduler(config_manager, db_manager)
    
    # 设置定时任务
    print("\n设置定时任务:")
    print("  - 销售报告: 每天 02:00 自动执行")
    print("  - 库存报告: 每天 03:00 自动执行")
    
    scheduler.schedule_sales_reports(time_str="02:00", days_ago=1)
    scheduler.schedule_inventory_reports(time_str="03:00", days_ago=1)
    
    # 启动调度器
    print("\n启动调度器...")
    scheduler.start()
    
    print("✅ 调度器已启动，按 Ctrl+C 停止")
    
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n停止调度器...")
        scheduler.stop()
        print("✅ 调度器已停止")


def example_5_query_data():
    """示例5: 查询MySQL中的数据"""
    print("\n" + "="*60)
    print("示例5: 查询MySQL中的数据")
    print("="*60)
    
    # MySQL配置
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'amazon_user',
        'password': '你的密码',
        'database': 'amazon_sp'
    }
    
    # 初始化数据库管理器
    db_manager = create_mysql_manager_from_config(mysql_config)
    
    # 查询销售数据
    print("\n查询最近7天的销售数据:")
    with db_manager.session_scope() as session:
        from app.models.mysql_models import SalesReport, Store
        from sqlalchemy import func
        from datetime import timedelta
        
        # 按店铺汇总
        results = session.query(
            Store.store_name,
            func.sum(SalesReport.units_ordered).label('total_units'),
            func.sum(SalesReport.ordered_product_sales).label('total_sales'),
            func.avg(SalesReport.buy_box_percentage).label('avg_buy_box')
        ).join(
            SalesReport, Store.store_id == SalesReport.store_id
        ).filter(
            SalesReport.report_date >= datetime.now() - timedelta(days=7)
        ).group_by(
            Store.store_name
        ).all()
        
        print("\n店铺销售汇总:")
        print(f"{'店铺名称':<20} {'订单数':>10} {'销售额':>15} {'Buy Box率':>12}")
        print("-" * 60)
        for row in results:
            print(f"{row.store_name:<20} {row.total_units:>10} ${row.total_sales:>14,.2f} {row.avg_buy_box:>11.2f}%")
    
    # 查询Top商品
    print("\n查询Top 10商品:")
    with db_manager.session_scope() as session:
        from app.models.mysql_models import SalesReportByASIN
        
        results = session.query(
            SalesReportByASIN.parent_asin,
            SalesReportByASIN.sku,
            func.sum(SalesReportByASIN.units_ordered).label('total_units'),
            func.sum(SalesReportByASIN.ordered_product_sales).label('total_sales')
        ).filter(
            SalesReportByASIN.report_date >= datetime.now() - timedelta(days=7)
        ).group_by(
            SalesReportByASIN.parent_asin,
            SalesReportByASIN.sku
        ).order_by(
            func.sum(SalesReportByASIN.units_ordered).desc()
        ).limit(10).all()
        
        print("\nTop 10 商品:")
        print(f"{'ASIN':<15} {'SKU':<20} {'销量':>10} {'销售额':>15}")
        print("-" * 65)
        for row in results:
            print(f"{row.parent_asin:<15} {row.sku:<20} {row.total_units:>10} ${row.total_sales:>14,.2f}")


def main():
    """主函数 - 显示菜单"""
    print("\n" + "="*60)
    print(" 亚马逊SP API Reports使用示例")
    print("="*60)
    print("\n选择一个示例运行:")
    print("  1. 手动获取销售报告")
    print("  2. 手动获取库存报告")
    print("  3. 获取单个店铺的报告")
    print("  4. 使用定时调度器")
    print("  5. 查询MySQL中的数据")
    print("  0. 退出")
    
    choice = input("\n请选择 (0-5): ")
    
    if choice == '1':
        example_1_manual_sales_report()
    elif choice == '2':
        example_2_manual_inventory_report()
    elif choice == '3':
        example_3_single_store_report()
    elif choice == '4':
        example_4_scheduled_reports()
    elif choice == '5':
        example_5_query_data()
    elif choice == '0':
        print("\n再见！")
    else:
        print("\n无效选择")


if __name__ == "__main__":
    main()