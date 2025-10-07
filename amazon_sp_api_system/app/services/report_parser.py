"""
报告解析器
将亚马逊报告数据解析为数据库模型
"""
import json
import logging
from datetime import datetime
from typing import List, Dict

from app.models.mysql_models import (
    SalesReport,
    SalesReportByASIN,
    InventoryReport,
    InventoryReportByASIN
)

logger = logging.getLogger(__name__)


class ReportParser:
    """报告解析器基类"""
    
    @staticmethod
    def safe_get(data: dict, *keys, default=None):
        """安全获取嵌套字典的值"""
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            else:
                return default
        return result if result is not None else default
    
    @staticmethod
    def parse_amount(amount_dict: dict) -> float:
        """解析金额对象"""
        if not amount_dict:
            return 0.0
        return float(amount_dict.get('amount', 0.0))
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                return datetime.utcnow()


class SalesReportParser(ReportParser):
    """销售和流量报告解析器"""
    
    @classmethod
    def parse(cls, store_id: str, report_content: bytes) -> Dict[str, List]:
        """
        解析销售和流量报告
        
        Args:
            store_id: 店铺ID
            report_content: 报告内容(JSON格式)
        
        Returns:
            字典，包含 'by_date' 和 'by_asin' 两个列表
        """
        try:
            # 解析JSON
            data = json.loads(report_content.decode('utf-8'))
            
            # 获取市场ID
            marketplace_id = cls.safe_get(
                data,
                'reportSpecification',
                'marketplaceIds',
                default=[]
            )
            marketplace_id = marketplace_id[0] if marketplace_id else None
            
            # 解析按日期汇总的数据
            by_date_reports = cls.parse_sales_by_date(
                store_id,
                marketplace_id,
                data.get('salesAndTrafficByDate', [])
            )
            
            # 解析按ASIN汇总的数据
            by_asin_reports = cls.parse_sales_by_asin(
                store_id,
                data.get('salesAndTrafficByAsin', [])
            )
            
            logger.info(f"销售报告解析完成: {len(by_date_reports)} 条按日期记录, {len(by_asin_reports)} 条按ASIN记录")
            
            return {
                'by_date': by_date_reports,
                'by_asin': by_asin_reports
            }
            
        except Exception as e:
            logger.error(f"解析销售报告失败: {e}")
            raise
    
    @classmethod
    def parse_sales_by_date(cls, store_id: str, marketplace_id: str, sales_data: list) -> List[SalesReport]:
        """解析按日期汇总的销售数据"""
        reports = []
        
        for item in sales_data:
            try:
                report_date = cls.parse_date(item.get('date'))
                sales_by_date = item.get('salesByDate', {})
                traffic_by_date = item.get('trafficByDate', {})
                
                report = SalesReport(
                    store_id=store_id,
                    report_date=report_date,
                    marketplace_id=marketplace_id,
                    
                    # 销售数据
                    ordered_product_sales=cls.parse_amount(sales_by_date.get('orderedProductSales')),
                    ordered_product_sales_b2b=cls.parse_amount(sales_by_date.get('orderedProductSalesB2B')),
                    units_ordered=sales_by_date.get('unitsOrdered', 0),
                    units_ordered_b2b=sales_by_date.get('unitsOrderedB2B', 0),
                    total_order_items=sales_by_date.get('totalOrderItems', 0),
                    total_order_items_b2b=sales_by_date.get('totalOrderItemsB2B', 0),
                    
                    average_sales_per_order_item=cls.parse_amount(sales_by_date.get('averageSalesPerOrderItem')),
                    average_units_per_order_item=sales_by_date.get('averageUnitsPerOrderItem', 0.0),
                    average_selling_price=cls.parse_amount(sales_by_date.get('averageSellingPrice')),
                    
                    units_refunded=sales_by_date.get('unitsRefunded', 0),
                    refund_rate=sales_by_date.get('refundRate', 0.0),
                    
                    claims_granted=sales_by_date.get('claimsGranted', 0),
                    claims_amount=cls.parse_amount(sales_by_date.get('claimsAmount')),
                    
                    shipped_product_sales=cls.parse_amount(sales_by_date.get('shippedProductSales')),
                    units_shipped=sales_by_date.get('unitsShipped', 0),
                    orders_shipped=sales_by_date.get('ordersShipped', 0),
                    
                    # 流量数据
                    browser_page_views=traffic_by_date.get('browserPageViews', 0),
                    mobile_app_page_views=traffic_by_date.get('mobileAppPageViews', 0),
                    page_views=traffic_by_date.get('pageViews', 0),
                    
                    browser_sessions=traffic_by_date.get('browserSessions', 0),
                    mobile_app_sessions=traffic_by_date.get('mobileAppSessions', 0),
                    sessions=traffic_by_date.get('sessions', 0),
                    
                    buy_box_percentage=traffic_by_date.get('buyBoxPercentage', 0.0),
                    order_item_session_percentage=traffic_by_date.get('orderItemSessionPercentage', 0.0),
                    unit_session_percentage=traffic_by_date.get('unitSessionPercentage', 0.0),
                    
                    average_offer_count=traffic_by_date.get('averageOfferCount', 0),
                    average_parent_items=traffic_by_date.get('averageParentItems', 0),
                    
                    feedback_received=traffic_by_date.get('feedbackReceived', 0),
                    negative_feedback_received=traffic_by_date.get('negativeFeedbackReceived', 0),
                    received_negative_feedback_rate=traffic_by_date.get('receivedNegativeFeedbackRate', 0.0),
                    
                    currency_code=cls.safe_get(sales_by_date, 'orderedProductSales', 'currencyCode', default='USD')
                )
                
                reports.append(report)
                
            except Exception as e:
                logger.error(f"解析单条销售数据失败: {e} - {item}")
                continue
        
        return reports
    
    @classmethod
    def parse_sales_by_asin(cls, store_id: str, asin_data: list) -> List[SalesReportByASIN]:
        """解析按ASIN汇总的销售数据"""
        reports = []
        
        # 使用当前日期作为报告日期
        report_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for item in asin_data:
            try:
                sales_by_asin = item.get('salesByAsin', {})
                traffic_by_asin = item.get('trafficByAsin', {})
                
                report = SalesReportByASIN(
                    store_id=store_id,
                    report_date=report_date,
                    
                    parent_asin=item.get('parentAsin'),
                    child_asin=item.get('childAsin'),
                    sku=item.get('sku'),
                    
                    # 销售数据
                    units_ordered=sales_by_asin.get('unitsOrdered', 0),
                    units_ordered_b2b=sales_by_asin.get('unitsOrderedB2B', 0),
                    ordered_product_sales=cls.parse_amount(sales_by_asin.get('orderedProductSales')),
                    ordered_product_sales_b2b=cls.parse_amount(sales_by_asin.get('orderedProductSalesB2B')),
                    total_order_items=sales_by_asin.get('totalOrderItems', 0),
                    total_order_items_b2b=sales_by_asin.get('totalOrderItemsB2B', 0),
                    
                    # 流量数据
                    browser_sessions=traffic_by_asin.get('browserSessions', 0),
                    mobile_app_sessions=traffic_by_asin.get('mobileAppSessions', 0),
                    sessions=traffic_by_asin.get('sessions', 0),
                    
                    browser_session_percentage=traffic_by_asin.get('browserSessionPercentage', 0.0),
                    mobile_app_session_percentage=traffic_by_asin.get('mobileAppSessionPercentage', 0.0),
                    session_percentage=traffic_by_asin.get('sessionPercentage', 0.0),
                    
                    browser_page_views=traffic_by_asin.get('browserPageViews', 0),
                    mobile_app_page_views=traffic_by_asin.get('mobileAppPageViews', 0),
                    page_views=traffic_by_asin.get('pageViews', 0),
                    
                    browser_page_views_percentage=traffic_by_asin.get('browserPageViewsPercentage', 0.0),
                    mobile_app_page_views_percentage=traffic_by_asin.get('mobileAppPageViewsPercentage', 0.0),
                    page_views_percentage=traffic_by_asin.get('pageViewsPercentage', 0.0),
                    
                    buy_box_percentage=traffic_by_asin.get('buyBoxPercentage', 0.0),
                    unit_session_percentage=traffic_by_asin.get('unitSessionPercentage', 0.0),
                    
                    currency_code=cls.safe_get(sales_by_asin, 'orderedProductSales', 'currencyCode', default='USD')
                )
                
                reports.append(report)
                
            except Exception as e:
                logger.error(f"解析单条ASIN数据失败: {e} - {item}")
                continue
        
        return reports


class InventoryReportParser(ReportParser):
    """库存报告解析器"""
    
    @classmethod
    def parse(cls, store_id: str, report_content: bytes) -> Dict[str, List]:
        """
        解析库存报告
        
        Args:
            store_id: 店铺ID
            report_content: 报告内容(JSON格式)
        
        Returns:
            字典，包含 'aggregate' 和 'by_asin' 两个列表
        """
        try:
            # 解析JSON
            data = json.loads(report_content.decode('utf-8'))
            
            # 获取市场ID
            marketplace_id = cls.safe_get(
                data,
                'reportSpecification',
                'marketplaceIds',
                default=[]
            )
            marketplace_id = marketplace_id[0] if marketplace_id else None
            
            # 解析汇总数据
            aggregate_reports = cls.parse_inventory_aggregate(
                store_id,
                marketplace_id,
                data.get('inventoryAggregate', [])
            )
            
            # 解析按ASIN的数据
            by_asin_reports = cls.parse_inventory_by_asin(
                store_id,
                data.get('inventoryByAsin', [])
            )
            
            logger.info(f"库存报告解析完成: {len(aggregate_reports)} 条汇总记录, {len(by_asin_reports)} 条ASIN记录")
            
            return {
                'aggregate': aggregate_reports,
                'by_asin': by_asin_reports
            }
            
        except Exception as e:
            logger.error(f"解析库存报告失败: {e}")
            raise
    
    @classmethod
    def parse_inventory_aggregate(cls, store_id: str, marketplace_id: str, inventory_data: list) -> List[InventoryReport]:
        """解析汇总库存数据"""
        reports = []
        
        for item in inventory_data:
            try:
                start_date = cls.parse_date(item.get('startDate'))
                end_date = cls.parse_date(item.get('endDate'))
                
                report = InventoryReport(
                    store_id=store_id,
                    report_start_date=start_date,
                    report_end_date=end_date,
                    marketplace_id=marketplace_id,
                    
                    vendor_confirmation_rate=item.get('vendorConfirmationRate', 0.0),
                    net_received_inventory_cost=cls.parse_amount(item.get('netReceivedInventoryCost')),
                    net_received_inventory_units=item.get('netReceivedInventoryUnits', 0),
                    open_purchase_order_units=item.get('openPurchaseOrderUnits', 0),
                    average_vendor_lead_time_days=item.get('averageVendorLeadTimeDays', 0.0),
                    
                    sell_through_rate=item.get('sellThroughRate', 0.0),
                    unfilled_customer_ordered_units=item.get('unfilledCustomerOrderedUnits', 0),
                    
                    sellable_on_hand_inventory_cost=cls.parse_amount(item.get('sellableOnHandInventoryCost')),
                    sellable_on_hand_inventory_units=item.get('sellableOnHandInventoryUnits', 0),
                    
                    unsellable_on_hand_inventory_cost=cls.parse_amount(item.get('unsellableOnHandInventoryCost')),
                    unsellable_on_hand_inventory_units=item.get('unsellableOnHandInventoryUnits', 0),
                    
                    aged_90_plus_days_sellable_inventory_cost=cls.parse_amount(item.get('aged90PlusDaysSellableInventoryCost')),
                    aged_90_plus_days_sellable_inventory_units=item.get('aged90PlusDaysSellableInventoryUnits', 0),
                    
                    unhealthy_inventory_cost=cls.parse_amount(item.get('unhealthyInventoryCost')),
                    unhealthy_inventory_units=item.get('unhealthyInventoryUnits', 0),
                    
                    procurable_product_out_of_stock_rate=item.get('procurableProductOutOfStockRate', 0.0),
                    uft=item.get('uft', 0.0),
                    receive_fill_rate=item.get('receiveFillRate', 0.0),
                    
                    currency_code=cls.safe_get(item, 'netReceivedInventoryCost', 'currencyCode', default='USD')
                )
                
                reports.append(report)
                
            except Exception as e:
                logger.error(f"解析单条库存数据失败: {e} - {item}")
                continue
        
        return reports
    
    @classmethod
    def parse_inventory_by_asin(cls, store_id: str, asin_data: list) -> List[InventoryReportByASIN]:
        """解析按ASIN的库存数据"""
        reports = []
        
        for item in asin_data:
            try:
                start_date = cls.parse_date(item.get('startDate'))
                end_date = cls.parse_date(item.get('endDate'))
                
                report = InventoryReportByASIN(
                    store_id=store_id,
                    report_start_date=start_date,
                    report_end_date=end_date,
                    
                    asin=item.get('asin'),
                    
                    vendor_confirmation_rate=item.get('vendorConfirmationRate', 0.0),
                    net_received_inventory_cost=cls.parse_amount(item.get('netReceivedInventoryCost')),
                    net_received_inventory_units=item.get('netReceivedInventoryUnits', 0),
                    open_purchase_order_units=item.get('openPurchaseOrderUnits', 0),
                    average_vendor_lead_time_days=item.get('averageVendorLeadTimeDays', 0.0),
                    sell_through_rate=item.get('sellThroughRate', 0.0),
                    unfilled_customer_ordered_units=item.get('unfilledCustomerOrderedUnits', 0),
                    sellable_on_hand_inventory_cost=cls.parse_amount(item.get('sellableOnHandInventoryCost')),
                    sellable_on_hand_inventory_units=item.get('sellableOnHandInventoryUnits', 0),
                    unsellable_on_hand_inventory_cost=cls.parse_amount(item.get('unsellableOnHandInventoryCost')),
                    unsellable_on_hand_inventory_units=item.get('unsellableOnHandInventoryUnits', 0),
                    aged_90_plus_days_sellable_inventory_cost=cls.parse_amount(item.get('aged90PlusDaysSellableInventoryCost')),
                    aged_90_plus_days_sellable_inventory_units=item.get('aged90PlusDaysSellableInventoryUnits', 0),
                    unhealthy_inventory_cost=cls.parse_amount(item.get('unhealthyInventoryCost')),
                    unhealthy_inventory_units=item.get('unhealthy InventoryUnits', 0),
                    procurable_product_out_of_stock_rate=item.get('procurableProductOutOfStockRate', 0.0),
                    uft=item.get('uft', 0.0),
                    receive_fill_rate=item.get('receiveFillRate', 0.0),
                    
                    currency_code=cls.safe_get(item, 'netReceivedInventoryCost', 'currencyCode', default='USD')
                )
                
                reports.append(report)
                
            except Exception as e:
                logger.error(f"解析单条ASIN库存数据失败: {e} - {item}")
                continue
        
        return reports