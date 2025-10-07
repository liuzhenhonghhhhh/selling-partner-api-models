"""
报告定时调度器
定时自动获取和处理报告数据
"""
import schedule
import time
import logging
from datetime import datetime
from typing import List
import threading

from app.config.sp_api_config import MultiStoreConfig
from app.models.mysql_manager import MySQLManager
from app.services.report_service import ReportProcessingService

logger = logging.getLogger(__name__)


class ReportScheduler:
    """报告定时调度器"""
    
    def __init__(
        self,
        config_manager: MultiStoreConfig,
        db_manager: MySQLManager
    ):
        """
        初始化调度器
        
        Args:
            config_manager: 店铺配置管理器
            db_manager: 数据库管理器
        """
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.report_service = ReportProcessingService(db_manager)
        self.running = False
        self.scheduler_thread = None
        
        logger.info("报告调度器初始化成功")
    
    def schedule_sales_reports(self, time_str: str = "02:00", days_ago: int = 1):
        """
        定时执行销售报告任务
        
        Args:
            time_str: 执行时间，格式 "HH:MM"
            days_ago: 获取多少天前的数据
        """
        def job():
            logger.info(f"开始执行定时销售报告任务: {datetime.now()}")
            stores = self.config_manager.get_all_stores()
            results = self.report_service.process_all_stores_sales(stores, days_ago=days_ago)
            
            success_count = sum(1 for r in results if r.get('success'))
            logger.info(f"销售报告任务完成: 成功 {success_count}/{len(results)}")
        
        schedule.every().day.at(time_str).do(job)
        logger.info(f"已设置销售报告定时任务: 每天 {time_str}")
    
    def schedule_inventory_reports(self, time_str: str = "03:00", days_ago: int = 1):
        """
        定时执行库存报告任务
        
        Args:
            time_str: 执行时间，格式 "HH:MM"
            days_ago: 获取多少天前的数据
        """
        def job():
            logger.info(f"开始执行定时库存报告任务: {datetime.now()}")
            stores = self.config_manager.get_all_stores()
            results = self.report_service.process_all_stores_inventory(stores, days_ago=days_ago)
            
            success_count = sum(1 for r in results if r.get('success'))
            logger.info(f"库存报告任务完成: 成功 {success_count}/{len(results)}")
        
        schedule.every().day.at(time_str).do(job)
        logger.info(f"已设置库存报告定时任务: 每天 {time_str}")
    
    def schedule_hourly_sales(self):
        """每小时执行销售报告"""
        def job():
            logger.info(f"开始执行每小时销售报告任务: {datetime.now()}")
            stores = self.config_manager.get_all_stores()
            results = self.report_service.process_all_stores_sales(stores, days_ago=1)
            
            success_count = sum(1 for r in results if r.get('success'))
            logger.info(f"每小时销售报告任务完成: 成功 {success_count}/{len(results)}")
        
        schedule.every().hour.do(job)
        logger.info("已设置每小时销售报告任务")
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return
        
        self.running = True
        
        def run_scheduler():
            logger.info("调度器线程启动")
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # 每分钟检查一次
                except Exception as e:
                    logger.error(f"调度器执行异常: {e}")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("报告调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("报告调度器已停止")
    
    def run_now_sales(self):
        """立即执行销售报告任务"""
        logger.info("立即执行销售报告任务")
        stores = self.config_manager.get_all_stores()
        return self.report_service.process_all_stores_sales(stores, days_ago=7)
    
    def run_now_inventory(self):
        """立即执行库存报告任务"""
        logger.info("立即执行库存报告任务")
        stores = self.config_manager.get_all_stores()
        return self.report_service.process_all_stores_inventory(stores, days_ago=7)