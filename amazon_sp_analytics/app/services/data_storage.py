"""
数据存储服务 - 按年月分表存储
"""
from datetime import datetime
from typing import List, Dict, Any
import json
from loguru import logger

from app.models.database import DatabaseManager, Store, MonitoringSnapshot, Alert, DailySummary


class DataStorageService:
    """数据存储服务"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def save_orders(self, orders: List[Dict[str, Any]], store_id: str) -> int:
        """
        批量保存订单数据（按年月分表）
        
        Args:
            orders: 订单列表
            store_id: 店铺ID
        
        Returns:
            成功保存的订单数
        """
        if not orders:
            return 0
        
        session = self.db_manager.get_session()
        saved_count = 0
        
        try:
            # 按年月分组
            orders_by_month = {}
            for order in orders:
                purchase_date = datetime.fromisoformat(
                    order['PurchaseDate'].replace('Z', '+00:00')
                )
                month_key = (purchase_date.year, purchase_date.month)
                
                if month_key not in orders_by_month:
                    orders_by_month[month_key] = []
                orders_by_month[month_key].append((order, purchase_date))
            
            # 逐月保存
            for (year, month), month_orders in orders_by_month.items():
                OrderTable = self.db_manager.get_month_table('orders', year, month)
                
                for order, purchase_date in month_orders:
                    try:
                        items = order.get('OrderItems', [])
                        
                        order_record = OrderTable(
                            store_id=store_id,
                            order_id=order['AmazonOrderId'],
                            marketplace_id=order.get('MarketplaceId', ''),
                            purchase_date=purchase_date,
                            last_update_date=datetime.fromisoformat(
                                order['LastUpdateDate'].replace('Z', '+00:00')
                            ) if 'LastUpdateDate' in order else None,
                            order_status=order.get('OrderStatus'),
                            fulfillment_channel=order.get('FulfillmentChannel'),
                            sales_channel=order.get('SalesChannel'),
                            order_total_amount=float(order.get('OrderTotal', {}).get('Amount', 0)),
                            order_total_currency=order.get('OrderTotal', {}).get('CurrencyCode', 'USD'),
                            buyer_email=order.get('BuyerEmail'),
                            buyer_name=order.get('BuyerName'),
                            ship_city=order.get('ShippingAddress', {}).get('City'),
                            ship_state=order.get('ShippingAddress', {}).get('StateOrRegion'),
                            ship_country=order.get('ShippingAddress', {}).get('CountryCode'),
                            ship_postal_code=order.get('ShippingAddress', {}).get('PostalCode'),
                            items=json.dumps(items, ensure_ascii=False)
                        )
                        
                        session.merge(order_record)
                        saved_count += 1
                        
                    except Exception as e:
                        logger.warning(f"保存订单失败: {e}")
                        continue
            
            session.commit()
            logger.success(f"成功保存 {saved_count}/{len(orders)} 个订单")
            return saved_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"批量保存订单失败: {e}")
            return 0
        finally:
            session.close()
    
    def save_sales_metrics(
        self,
        metrics: List[Dict[str, Any]],
        store_id: str,
        marketplace_id: str
    ) -> int:
        """批量保存销售指标（按年月分表）"""
        if not metrics:
            return 0
        
        session = self.db_manager.get_session()
        saved_count = 0
        
        try:
            metrics_by_month = {}
            for metric in metrics:
                interval = metric.get('interval', '')
                if not interval:
                    continue
                
                interval_parts = interval.split('--')
                if len(interval_parts) != 2:
                    continue
                
                start_time = datetime.fromisoformat(interval_parts[0].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(interval_parts[1].replace('Z', '+00:00'))
                month_key = (start_time.year, start_time.month)
                
                if month_key not in metrics_by_month:
                    metrics_by_month[month_key] = []
                metrics_by_month[month_key].append((metric, start_time, end_time))
            
            for (year, month), month_metrics in metrics_by_month.items():
                SalesMetricTable = self.db_manager.get_month_table('sales_metrics', year, month)
                
                for metric, start_time, end_time in month_metrics:
                    try:
                        total_sales = metric.get('totalSales', {})
                        
                        metric_record = SalesMetricTable(
                            store_id=store_id,
                            marketplace_id=marketplace_id,
                            interval_start=start_time,
                            interval_end=end_time,
                            granularity=metric.get('granularity', 'Hour'),
                            order_count=metric.get('orderCount', 0),
                            unit_count=metric.get('unitCount', 0),
                            total_sales_amount=float(total_sales.get('amount', 0)),
                            total_sales_currency=total_sales.get('currencyCode', 'USD'),
                            average_order_value=metric.get('averageOrderValue', 0),
                            average_units_per_order=metric.get('averageUnitsPerOrder', 0),
                            buyer_type=metric.get('buyerType', 'All')
                        )
                        
                        session.merge(metric_record)
                        saved_count += 1
                        
                    except Exception as e:
                        logger.warning(f"保存销售指标失败: {e}")
                        continue
            
            session.commit()
            logger.success(f"成功保存 {saved_count} 个销售指标")
            return saved_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"批量保存销售指标失败: {e}")
            return 0
        finally:
            session.close()
    
    def save_financial_events(self, events: Dict[str, List], store_id: str) -> int:
        """保存财务事件（按年月分表）"""
        session = self.db_manager.get_session()
        saved_count = 0
        
        try:
            for event in events.get('ShipmentEventList', []):
                posted_date = datetime.fromisoformat(
                    event['PostedDate'].replace('Z', '+00:00')
                ) if 'PostedDate' in event else datetime.now()
                
                year, month = posted_date.year, posted_date.month
                FinancialEventTable = self.db_manager.get_month_table('financial_events', year, month)
                
                revenue = 0
                fees = 0
                revenue_breakdown = {}
                fee_breakdown = {}
                
                for item in event.get('ShipmentItemList', []):
                    for charge in item.get('ItemChargeList', []):
                        amount = float(charge.get('ChargeAmount', {}).get('CurrencyAmount', 0))
                        charge_type = charge.get('ChargeType', 'Unknown')
                        revenue += amount
                        revenue_breakdown[charge_type] = revenue_breakdown.get(charge_type, 0) + amount
                    
                    for fee in item.get('ItemFeeList', []):
                        amount = abs(float(fee.get('FeeAmount', {}).get('CurrencyAmount', 0)))
                        fee_type = fee.get('FeeType', 'Unknown')
                        fees += amount
                        fee_breakdown[fee_type] = fee_breakdown.get(fee_type, 0) + amount
                
                event_record = FinancialEventTable(
                    store_id=store_id,
                    event_type='Shipment',
                    posted_date=posted_date,
                    order_id=event.get('AmazonOrderId'),
                    marketplace_id=event.get('MarketplaceId'),
                    revenue_amount=revenue,
                    fee_amount=fees,
                    currency_code='USD',
                    revenue_breakdown=json.dumps(revenue_breakdown, ensure_ascii=False),
                    fee_breakdown=json.dumps(fee_breakdown, ensure_ascii=False)
                )
                
                session.add(event_record)
                saved_count += 1
            
            session.commit()
            logger.success(f"成功保存 {saved_count} 个财务事件")
            return saved_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存财务事件失败: {e}")
            return 0
        finally:
            session.close()
    
    def save_monitoring_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        """保存监控快照"""
        session = self.db_manager.get_session()
        try:
            snapshot = MonitoringSnapshot(
                snapshot_time=datetime.now(),
                total_stores=snapshot_data.get('total_stores', 0),
                total_orders_1h=snapshot_data.get('total_orders_1h', 0),
                total_revenue_1h=snapshot_data.get('total_revenue_1h', 0),
                total_revenue_24h=snapshot_data.get('total_revenue_24h', 0),
                total_profit_7d=snapshot_data.get('total_profit_7d', 0),
                orders_per_hour=snapshot_data.get('orders_per_hour', 0),
                revenue_per_hour=snapshot_data.get('revenue_per_hour', 0),
                average_order_value=snapshot_data.get('average_order_value', 0),
                average_profit_margin=snapshot_data.get('average_profit_margin', 0),
                store_metrics=json.dumps(snapshot_data.get('store_metrics', []), ensure_ascii=False)
            )
            
            session.add(snapshot)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存监控快照失败: {e}")
            return False
        finally:
            session.close()
    
    def save_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """保存每日汇总"""
        session = self.db_manager.get_session()
        try:
            summary = DailySummary(
                store_id=summary_data['store_id'],
                summary_date=summary_data['summary_date'],
                total_orders=summary_data.get('total_orders', 0),
                total_units=summary_data.get('total_units', 0),
                total_revenue=summary_data.get('total_revenue', 0),
                average_order_value=summary_data.get('average_order_value', 0),
                total_fees=summary_data.get('total_fees', 0),
                total_refunds=summary_data.get('total_refunds', 0),
                net_profit=summary_data.get('net_profit', 0),
                profit_margin=summary_data.get('profit_margin', 0),
                order_status_distribution=json.dumps(
                    summary_data.get('order_status_distribution', {}),
                    ensure_ascii=False
                ),
                afn_orders=summary_data.get('afn_orders', 0),
                mfn_orders=summary_data.get('mfn_orders', 0)
            )
            
            session.merge(summary)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存每日汇总失败: {e}")
            return False
        finally:
            session.close()