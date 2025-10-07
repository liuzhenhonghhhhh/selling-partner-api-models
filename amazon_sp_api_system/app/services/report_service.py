"""
报告处理服务
整合Reports API客户端、解析器和数据库存储
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from app.config.sp_api_config import StoreCredentials
from app.core.reports_client import ReportsAPIClient, ReportType
from app.services.report_parser import SalesReportParser, InventoryReportParser
from app.models.mysql_manager import MySQLManager
from app.models.mysql_models import ReportRequest

logger = logging.getLogger(__name__)


class ReportProcessingService:
    """报告处理服务"""
    
    def __init__(self, db_manager: MySQLManager):
        """
        初始化报告处理服务
        
        Args:
            db_manager: MySQL数据库管理器
        """
        self.db_manager = db_manager
        logger.info("报告处理服务初始化成功")
    
    def process_sales_report(
        self,
        credentials: StoreCredentials,
        days_ago: int = 7,
        date_granularity: str = "DAY",
        asin_granularity: str = "SKU"
    ) -> dict:
        """
        处理销售和流量报告
        
        Args:
            credentials: 店铺凭证
            days_ago: 获取多少天前的数据
            date_granularity: 日期粒度 (DAY/WEEK/MONTH)
            asin_granularity: ASIN粒度 (PARENT/CHILD/SKU)
        
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"开始处理销售报告: {credentials.store_id}, 最近{days_ago}天")
            
            # 1. 创建Reports API客户端
            client = ReportsAPIClient(credentials)
            
            # 2. 确定时间范围
            data_end_time = datetime.utcnow()
            data_start_time = data_end_time - timedelta(days=days_ago)
            
            # 3. 创建报告请求
            report_options = {
                "dateGranularity": date_granularity,
                "asinGranularity": asin_granularity
            }
            
            create_result = client.create_report(
                ReportType.SALES_AND_TRAFFIC.value,
                credentials.marketplace_ids,
                data_start_time,
                data_end_time,
                report_options
            )
            
            report_id = create_result.get("reportId")
            
            # 4. 保存报告请求记录
            with self.db_manager.session_scope() as session:
                report_request = ReportRequest(
                    store_id=credentials.store_id,
                    report_type=ReportType.SALES_AND_TRAFFIC.value,
                    report_id=report_id,
                    data_start_time=data_start_time,
                    data_end_time=data_end_time,
                    marketplace_ids=credentials.marketplace_ids,
                    report_options=report_options,
                    status='IN_QUEUE',
                    requested_at=datetime.utcnow()
                )
                session.add(report_request)
            
            # 5. 等待报告完成
            logger.info(f"等待报告生成: {report_id}")
            report = client.wait_for_report_completion(report_id)
            
            # 6. 更新报告状态
            self.db_manager.update_report_request(report_id, {
                'status': 'DONE',
                'processing_ended_at': datetime.utcnow(),
                'report_document_id': report.get('reportDocumentId')
            })
            
            # 7. 获取并下载报告
            report_document_id = report.get('reportDocumentId')
            document = client.get_report_document(report_document_id)
            
            document_url = document.get('url')
            compression = document.get('compressionAlgorithm')
            
            logger.info(f"下载报告: {report_document_id}")
            content = client.download_report(document_url, compression)
            
            self.db_manager.update_report_request(report_id, {
                'downloaded_at': datetime.utcnow(),
                'document_url': document_url,
                'compression_algorithm': compression
            })
            
            # 8. 解析报告数据
            logger.info("解析报告数据...")
            parsed_data = SalesReportParser.parse(credentials.store_id, content)
            
            # 9. 存入数据库
            logger.info("保存数据到数据库...")
            with self.db_manager.session_scope() as session:
                # 保存按日期汇总的数据
                for report in parsed_data['by_date']:
                    session.merge(report)  # 使用merge避免重复
                
                # 保存按ASIN的数据
                for report in parsed_data['by_asin']:
                    session.merge(report)
            
            self.db_manager.update_report_request(report_id, {
                'parsed_at': datetime.utcnow()
            })
            
            logger.info(f"销售报告处理完成: {len(parsed_data['by_date'])} 条日期记录, {len(parsed_data['by_asin'])} 条ASIN记录")
            
            return {
                'success': True,
                'report_id': report_id,
                'records_by_date': len(parsed_data['by_date']),
                'records_by_asin': len(parsed_data['by_asin'])
            }
            
        except Exception as e:
            logger.error(f"处理销售报告失败: {e}")
            
            # 更新错误状态
            if 'report_id' in locals():
                self.db_manager.update_report_request(report_id, {
                    'status': 'FATAL',
                    'error_message': str(e)
                })
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_inventory_report(
        self,
        credentials: StoreCredentials,
        days_ago: int = 7,
        report_period: str = "DAY"
    ) -> dict:
        """
        处理库存报告
        
        Args:
            credentials: 店铺凭证
            days_ago: 获取多少天前的数据
            report_period: 报告周期 (DAY/WEEK/MONTH)
        
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"开始处理库存报告: {credentials.store_id}, 最近{days_ago}天")
            
            # 1. 创建Reports API客户端
            client = ReportsAPIClient(credentials)
            
            # 2. 确定时间范围
            data_end_time = datetime.utcnow()
            data_start_time = data_end_time - timedelta(days=days_ago)
            
            # 3. 创建报告请求
            report_options = {
                "reportPeriod": report_period,
                "distributorView": "MANUFACTURING",
                "sellingProgram": "RETAIL"
            }
            
            create_result = client.create_report(
                ReportType.VENDOR_INVENTORY.value,
                credentials.marketplace_ids,
                data_start_time,
                data_end_time,
                report_options
            )
            
            report_id = create_result.get("reportId")
            
            # 4. 保存报告请求记录
            with self.db_manager.session_scope() as session:
                report_request = ReportRequest(
                    store_id=credentials.store_id,
                    report_type=ReportType.VENDOR_INVENTORY.value,
                    report_id=report_id,
                    data_start_time=data_start_time,
                    data_end_time=data_end_time,
                    marketplace_ids=credentials.marketplace_ids,
                    report_options=report_options,
                    status='IN_QUEUE',
                    requested_at=datetime.utcnow()
                )
                session.add(report_request)
            
            # 5. 等待报告完成
            logger.info(f"等待报告生成: {report_id}")
            report = client.wait_for_report_completion(report_id)
            
            # 6. 更新报告状态
            self.db_manager.update_report_request(report_id, {
                'status': 'DONE',
                'processing_ended_at': datetime.utcnow(),
                'report_document_id': report.get('reportDocumentId')
            })
            
            # 7. 获取并下载报告
            report_document_id = report.get('reportDocumentId')
            document = client.get_report_document(report_document_id)
            
            document_url = document.get('url')
            compression = document.get('compressionAlgorithm')
            
            logger.info(f"下载报告: {report_document_id}")
            content = client.download_report(document_url, compression)
            
            self.db_manager.update_report_request(report_id, {
                'downloaded_at': datetime.utcnow(),
                'document_url': document_url,
                'compression_algorithm': compression
            })
            
            # 8. 解析报告数据
            logger.info("解析报告数据...")
            parsed_data = InventoryReportParser.parse(credentials.store_id, content)
            
            # 9. 存入数据库
            logger.info("保存数据到数据库...")
            with self.db_manager.session_scope() as session:
                # 保存汇总数据
                for report in parsed_data['aggregate']:
                    session.merge(report)
                
                # 保存按ASIN的数据
                for report in parsed_data['by_asin']:
                    session.merge(report)
            
            self.db_manager.update_report_request(report_id, {
                'parsed_at': datetime.utcnow()
            })
            
            logger.info(f"库存报告处理完成: {len(parsed_data['aggregate'])} 条汇总记录, {len(parsed_data['by_asin'])} 条ASIN记录")
            
            return {
                'success': True,
                'report_id': report_id,
                'records_aggregate': len(parsed_data['aggregate']),
                'records_by_asin': len(parsed_data['by_asin'])
            }
            
        except Exception as e:
            logger.error(f"处理库存报告失败: {e}")
            
            # 更新错误状态
            if 'report_id' in locals():
                self.db_manager.update_report_request(report_id, {
                    'status': 'FATAL',
                    'error_message': str(e)
                })
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_all_stores_sales(
        self,
        stores: List[StoreCredentials],
        days_ago: int = 7
    ) -> List[dict]:
        """
        处理所有店铺的销售报告
        
        Args:
            stores: 店铺凭证列表
            days_ago: 获取多少天前的数据
        
        Returns:
            处理结果列表
        """
        results = []
        
        for store in stores:
            try:
                logger.info(f"处理店铺: {store.store_name}")
                result = self.process_sales_report(store, days_ago=days_ago)
                result['store_id'] = store.store_id
                result['store_name'] = store.store_name
                results.append(result)
            except Exception as e:
                logger.error(f"处理店铺 {store.store_id} 失败: {e}")
                results.append({
                    'store_id': store.store_id,
                    'store_name': store.store_name,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def process_all_stores_inventory(
        self,
        stores: List[StoreCredentials],
        days_ago: int = 7
    ) -> List[dict]:
        """
        处理所有店铺的库存报告
        
        Args:
            stores: 店铺凭证列表
            days_ago: 获取多少天前的数据
        
        Returns:
            处理结果列表
        """
        results = []
        
        for store in stores:
            try:
                logger.info(f"处理店铺: {store.store_name}")
                result = self.process_inventory_report(store, days_ago=days_ago)
                result['store_id'] = store.store_id
                result['store_name'] = store.store_name
                results.append(result)
            except Exception as e:
                logger.error(f"处理店铺 {store.store_id} 失败: {e}")
                results.append({
                    'store_id': store.store_id,
                    'store_name': store.store_name,
                    'success': False,
                    'error': str(e)
                })
        
        return results