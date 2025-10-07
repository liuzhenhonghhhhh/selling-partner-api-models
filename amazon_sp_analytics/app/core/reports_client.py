"""
SP API Reports客户端
用于请求、查询和下载报告
"""
import requests
import json
import gzip
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum

from app.config.sp_api_config import StoreCredentials, Region
from app.core.sp_client import SPAPIClient

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    """报告类型枚举"""
    # 销售和流量报告
    SALES_AND_TRAFFIC = "GET_SALES_AND_TRAFFIC_REPORT"
    
    # 库存报告  
    VENDOR_INVENTORY = "GET_VENDOR_INVENTORY_REPORT"
    FBA_INVENTORY = "GET_FBA_INVENTORY_AGED_DATA"
    
    # 订单报告
    ALL_ORDERS = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    
    # 财务报告
    FINANCIAL_EVENTS = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"


class ReportStatus(str, Enum):
    """报告状态"""
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    FATAL = "FATAL"
    IN_PROGRESS = "IN_PROGRESS"
    IN_QUEUE = "IN_QUEUE"


class ReportsAPIClient:
    """Reports API客户端"""
    
    def __init__(self, credentials: StoreCredentials):
        """
        初始化Reports API客户端
        
        Args:
            credentials: 店铺凭证
        """
        self.credentials = credentials
        self.sp_client = SPAPIClient(credentials)
        self.base_path = "/reports/2021-06-30"
        
        logger.info(f"Reports API客户端初始化: {credentials.store_id}")
    
    def create_report(
        self,
        report_type: str,
        marketplace_ids: List[str],
        data_start_time: Optional[datetime] = None,
        data_end_time: Optional[datetime] = None,
        report_options: Optional[Dict] = None
    ) -> Dict:
        """
        创建报告请求
        
        Args:
            report_type: 报告类型
            marketplace_ids: Marketplace ID列表
            data_start_time: 数据开始时间
            data_end_time: 数据结束时间
            report_options: 报告选项
        
        Returns:
            包含reportId的字典
        """
        endpoint = f"{self.base_path}/reports"
        
        # 准备请求体
        body = {
            "reportType": report_type,
            "marketplaceIds": marketplace_ids
        }
        
        if data_start_time:
            body["dataStartTime"] = data_start_time.isoformat()
        
        if data_end_time:
            body["dataEndTime"] = data_end_time.isoformat()
        
        if report_options:
            body["reportOptions"] = report_options
        
        try:
            response = self.sp_client.make_request("POST", endpoint, json=body)
            
            if response.status_code == 202:
                result = response.json()
                logger.info(f"报告创建成功: {result.get('reportId')}")
                return result
            else:
                logger.error(f"报告创建失败: {response.status_code} - {response.text}")
                raise Exception(f"创建报告失败: {response.text}")
                
        except Exception as e:
            logger.error(f"创建报告异常: {e}")
            raise
    
    def get_report(self, report_id: str) -> Dict:
        """
        获取报告详情
        
        Args:
            report_id: 报告ID
        
        Returns:
            报告详情字典
        """
        endpoint = f"{self.base_path}/reports/{report_id}"
        
        try:
            response = self.sp_client.make_request("GET", endpoint)
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"获取报告详情成功: {report_id}")
                return result
            else:
                logger.error(f"获取报告详情失败: {response.status_code} - {response.text}")
                raise Exception(f"获取报告失败: {response.text}")
                
        except Exception as e:
            logger.error(f"获取报告详情异常: {e}")
            raise
    
    def get_reports(
        self,
        report_types: Optional[List[str]] = None,
        processing_statuses: Optional[List[str]] = None,
        marketplace_ids: Optional[List[str]] = None,
        page_size: int = 10,
        created_since: Optional[datetime] = None,
        created_until: Optional[datetime] = None
    ) -> Dict:
        """
        获取报告列表
        
        Args:
            report_types: 报告类型列表
            processing_statuses: 处理状态列表
            marketplace_ids: Marketplace ID列表
            page_size: 每页数量
            created_since: 创建时间起始
            created_until: 创建时间结束
        
        Returns:
            包含reports列表的字典
        """
        endpoint = f"{self.base_path}/reports"
        
        params = {"pageSize": page_size}
        
        if report_types:
            params["reportTypes"] = ",".join(report_types)
        
        if processing_statuses:
            params["processingStatuses"] = ",".join(processing_statuses)
        
        if marketplace_ids:
            params["marketplaceIds"] = ",".join(marketplace_ids)
        
        if created_since:
            params["createdSince"] = created_since.isoformat()
        
        if created_until:
            params["createdUntil"] = created_until.isoformat()
        
        try:
            response = self.sp_client.make_request("GET", endpoint, params=params)
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"获取报告列表成功，数量: {len(result.get('reports', []))}")
                return result
            else:
                logger.error(f"获取报告列表失败: {response.status_code} - {response.text}")
                raise Exception(f"获取报告列表失败: {response.text}")
                
        except Exception as e:
            logger.error(f"获取报告列表异常: {e}")
            raise
    
    def get_report_document(self, report_document_id: str) -> Dict:
        """
        获取报告文档信息
        
        Args:
            report_document_id: 报告文档ID
        
        Returns:
            包含文档URL的字典
        """
        endpoint = f"{self.base_path}/documents/{report_document_id}"
        
        try:
            response = self.sp_client.make_request("GET", endpoint)
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"获取报告文档信息成功: {report_document_id}")
                return result
            else:
                logger.error(f"获取报告文档信息失败: {response.status_code} - {response.text}")
                raise Exception(f"获取报告文档失败: {response.text}")
                
        except Exception as e:
            logger.error(f"获取报告文档异常: {e}")
            raise
    
    def download_report(self, document_url: str, compression: Optional[str] = None) -> bytes:
        """
        下载报告内容
        
        Args:
            document_url: 文档下载URL
            compression: 压缩算法 (GZIP等)
        
        Returns:
            报告内容(bytes)
        """
        try:
            response = requests.get(document_url, timeout=300)
            
            if response.status_code == 200:
                content = response.content
                
                # 如果是GZIP压缩，解压缩
                if compression == "GZIP":
                    content = gzip.decompress(content)
                
                logger.info(f"报告下载成功，大小: {len(content)} bytes")
                return content
            else:
                logger.error(f"下载报告失败: {response.status_code}")
                raise Exception(f"下载报告失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"下载报告异常: {e}")
            raise
    
    def wait_for_report_completion(
        self,
        report_id: str,
        max_wait_time: int = 600,
        check_interval: int = 30
    ) -> Dict:
        """
        等待报告生成完成
        
        Args:
            report_id: 报告ID
            max_wait_time: 最大等待时间(秒)
            check_interval: 检查间隔(秒)
        
        Returns:
            完成的报告详情
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            report = self.get_report(report_id)
            status = report.get("processingStatus")
            
            logger.info(f"报告状态: {status} - {report_id}")
            
            if status == ReportStatus.DONE.value:
                logger.info(f"报告生成完成: {report_id}")
                return report
            elif status in [ReportStatus.CANCELLED.value, ReportStatus.FATAL.value]:
                logger.error(f"报告生成失败: {status}")
                raise Exception(f"报告生成失败: {status}")
            
            time.sleep(check_interval)
        
        raise TimeoutError(f"报告生成超时: {report_id}")
    
    def create_and_download_report(
        self,
        report_type: str,
        marketplace_ids: List[str],
        data_start_time: Optional[datetime] = None,
        data_end_time: Optional[datetime] = None,
        report_options: Optional[Dict] = None,
        max_wait_time: int = 600
    ) -> bytes:
        """
        一站式创建并下载报告
        
        Args:
            report_type: 报告类型
            marketplace_ids: Marketplace ID列表
            data_start_time: 数据开始时间
            data_end_time: 数据结束时间
            report_options: 报告选项
            max_wait_time: 最大等待时间(秒)
        
        Returns:
            报告内容(bytes)
        """
        # 1. 创建报告请求
        logger.info(f"开始创建报告: {report_type}")
        create_result = self.create_report(
            report_type,
            marketplace_ids,
            data_start_time,
            data_end_time,
            report_options
        )
        
        report_id = create_result.get("reportId")
        
        # 2. 等待报告完成
        logger.info(f"等待报告生成: {report_id}")
        report = self.wait_for_report_completion(report_id, max_wait_time)
        
        # 3. 获取文档信息
        report_document_id = report.get("reportDocumentId")
        logger.info(f"获取报告文档: {report_document_id}")
        document = self.get_report_document(report_document_id)
        
        # 4. 下载报告
        document_url = document.get("url")
        compression = document.get("compressionAlgorithm")
        logger.info(f"下载报告内容...")
        content = self.download_report(document_url, compression)
        
        return content
    
    # ========== 便捷方法 ==========
    
    def create_sales_and_traffic_report(
        self,
        marketplace_ids: List[str],
        days_ago: int = 7,
        date_granularity: str = "DAY",
        asin_granularity: str = "SKU"
    ) -> Dict:
        """
        创建销售和流量报告
        
        Args:
            marketplace_ids: Marketplace ID列表
            days_ago: 获取多少天前的数据
            date_granularity: 日期粒度 (DAY/WEEK/MONTH)
            asin_granularity: ASIN粒度 (PARENT/CHILD/SKU)
        
        Returns:
            报告创建结果
        """
        data_end_time = datetime.utcnow()
        data_start_time = data_end_time - timedelta(days=days_ago)
        
        report_options = {
            "dateGranularity": date_granularity,
            "asinGranularity": asin_granularity
        }
        
        return self.create_report(
            ReportType.SALES_AND_TRAFFIC.value,
            marketplace_ids,
            data_start_time,
            data_end_time,
            report_options
        )
    
    def create_inventory_report(
        self,
        marketplace_ids: List[str],
        days_ago: int = 7,
        report_period: str = "DAY"
    ) -> Dict:
        """
        创建库存报告
        
        Args:
            marketplace_ids: Marketplace ID列表
            days_ago: 获取多少天前的数据
            report_period: 报告周期 (DAY/WEEK/MONTH)
        
        Returns:
            报告创建结果
        """
        data_end_time = datetime.utcnow()
        data_start_time = data_end_time - timedelta(days=days_ago)
        
        report_options = {
            "reportPeriod": report_period,
            "distributorView": "MANUFACTURING",
            "sellingProgram": "RETAIL"
        }
        
        return self.create_report(
            ReportType.VENDOR_INVENTORY.value,
            marketplace_ids,
            data_start_time,
            data_end_time,
            report_options
        )