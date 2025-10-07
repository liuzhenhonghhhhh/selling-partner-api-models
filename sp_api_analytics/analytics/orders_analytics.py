"""
订单数据分析模块
支持实时订单监控、订单统计分析
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from loguru import logger

from core.sp_client import SPAPIClient


class OrdersAnalytics:
    """订单数据分析器"""
    
    def __init__(self, client: SPAPIClient):
        self.client = client
        self.store_id = client.credentials.store_id
        self.store_name = client.credentials.store_name
    
    def get_orders(
        self,
        marketplace_ids: List[str],
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        last_updated_after: Optional[str] = None,
        order_statuses: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取订单列表
        
        Args:
            marketplace_ids: 市场ID列表
            created_after: 创建时间之后 (ISO 8601格式)
            created_before: 创建时间之前
            last_updated_after: 最后更新时间之后
            order_statuses: 订单状态列表
            max_results: 最大返回数量
        
        Returns:
            订单列表
        """
        endpoint = "/orders/v0/orders"
        
        params = {
            "MarketplaceIds": ",".join(marketplace_ids),
        }
        
        if created_after:
            params["CreatedAfter"] = created_after
        if created_before:
            params["CreatedBefore"] = created_before
        if last_updated_after:
            params["LastUpdatedAfter"] = last_updated_after
        if order_statuses:
            params["OrderStatuses"] = ",".join(order_statuses)
        
        all_orders = []
        next_token = None
        
        logger.info(f"[{self.store_name}] 获取订单数据...")
        
        while True:
            if next_token:
                params["NextToken"] = next_token
            
            try:
                response = self.client.get(endpoint, params=params)
                
                if "payload" in response and "Orders" in response["payload"]:
                    orders = response["payload"]["Orders"]
                    all_orders.extend(orders)
                    
                    logger.info(f"[{self.store_name}] 已获取 {len(orders)} 个订单")
                    
                    # 检查是否达到最大数量
                    if len(all_orders) >= max_results:
                        all_orders = all_orders[:max_results]
                        break
                    
                    # 检查是否有下一页
                    next_token = response["payload"].get("NextToken")
                    if not next_token:
                        break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"[{self.store_name}] 获取订单失败: {e}")
                break
        
        logger.success(f"[{self.store_name}] 共获取 {len(all_orders)} 个订单")
        return all_orders
    
    def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详情
        """
        endpoint = f"/orders/v0/orders/{order_id}"
        
        try:
            response = self.client.get(endpoint)
            if "payload" in response:
                return response["payload"]
        except Exception as e:
            logger.error(f"[{self.store_name}] 获取订单 {order_id} 详情失败: {e}")
        
        return None
    
    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        """
        获取订单商品列表
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单商品列表
        """
        endpoint = f"/orders/v0/orders/{order_id}/orderItems"
        
        all_items = []
        next_token = None
        
        while True:
            params = {}
            if next_token:
                params["NextToken"] = next_token
            
            try:
                response = self.client.get(endpoint, params=params)
                
                if "payload" in response and "OrderItems" in response["payload"]:
                    items = response["payload"]["OrderItems"]
                    all_items.extend(items)
                    
                    next_token = response["payload"].get("NextToken")
                    if not next_token:
                        break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"[{self.store_name}] 获取订单 {order_id} 商品失败: {e}")
                break
        
        return all_items
    
    def get_recent_orders(
        self,
        marketplace_ids: List[str],
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        获取最近N小时的订单
        
        Args:
            marketplace_ids: 市场ID列表
            hours: 小时数
        
        Returns:
            订单列表
        """
        created_after = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"
        return self.get_orders(
            marketplace_ids=marketplace_ids,
            created_after=created_after
        )
    
    def analyze_orders(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析订单数据
        
        Args:
            orders: 订单列表
        
        Returns:
            分析结果
        """
        if not orders:
            return {
                "total_orders": 0,
                "total_amount": 0,
                "average_order_value": 0,
                "orders_by_status": {},
                "orders_by_channel": {},
            }
        
        # 转换为DataFrame便于分析
        df = pd.DataFrame(orders)
        
        # 基本统计
        total_orders = len(orders)
        
        # 计算总金额（需要处理OrderTotal字段）
        total_amount = 0
        valid_amounts = []
        for order in orders:
            if "OrderTotal" in order and "Amount" in order["OrderTotal"]:
                try:
                    amount = float(order["OrderTotal"]["Amount"])
                    valid_amounts.append(amount)
                    total_amount += amount
                except (ValueError, TypeError):
                    pass
        
        average_order_value = total_amount / len(valid_amounts) if valid_amounts else 0
        
        # 按状态统计
        orders_by_status = df["OrderStatus"].value_counts().to_dict() if "OrderStatus" in df.columns else {}
        
        # 按渠道统计
        orders_by_channel = df["FulfillmentChannel"].value_counts().to_dict() if "FulfillmentChannel" in df.columns else {}
        
        # 时间分布分析
        if "PurchaseDate" in df.columns:
            df["PurchaseDate"] = pd.to_datetime(df["PurchaseDate"])
            df["Hour"] = df["PurchaseDate"].dt.hour
            orders_by_hour = df["Hour"].value_counts().sort_index().to_dict()
        else:
            orders_by_hour = {}
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "total_orders": total_orders,
            "total_amount": round(total_amount, 2),
            "average_order_value": round(average_order_value, 2),
            "currency": orders[0].get("OrderTotal", {}).get("CurrencyCode", "USD") if orders else "USD",
            "orders_by_status": orders_by_status,
            "orders_by_channel": orders_by_channel,
            "orders_by_hour": orders_by_hour,
            "analysis_time": datetime.now().isoformat(),
        }
    
    def get_order_metrics_realtime(
        self,
        marketplace_ids: List[str],
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        获取实时订单指标（适用于分钟级监控）
        
        Args:
            marketplace_ids: 市场ID列表
            time_window_minutes: 时间窗口（分钟）
        
        Returns:
            实时订单指标
        """
        # 获取指定时间窗口内的订单
        created_after = (
            datetime.utcnow() - timedelta(minutes=time_window_minutes)
        ).isoformat() + "Z"
        
        orders = self.get_orders(
            marketplace_ids=marketplace_ids,
            created_after=created_after
        )
        
        # 分析订单
        analysis = self.analyze_orders(orders)
        
        # 添加实时指标
        analysis.update({
            "time_window_minutes": time_window_minutes,
            "orders_per_hour": round(len(orders) / (time_window_minutes / 60), 2),
            "revenue_per_hour": round(analysis["total_amount"] / (time_window_minutes / 60), 2),
        })
        
        return analysis
    
    def compare_with_previous_period(
        self,
        marketplace_ids: List[str],
        current_hours: int = 24
    ) -> Dict[str, Any]:
        """
        对比当前周期与前一周期的订单数据
        
        Args:
            marketplace_ids: 市场ID列表
            current_hours: 当前周期小时数
        
        Returns:
            对比分析结果
        """
        # 当前周期
        current_start = datetime.utcnow() - timedelta(hours=current_hours)
        current_orders = self.get_orders(
            marketplace_ids=marketplace_ids,
            created_after=current_start.isoformat() + "Z"
        )
        current_analysis = self.analyze_orders(current_orders)
        
        # 前一周期
        previous_start = current_start - timedelta(hours=current_hours)
        previous_end = current_start
        previous_orders = self.get_orders(
            marketplace_ids=marketplace_ids,
            created_after=previous_start.isoformat() + "Z",
            created_before=previous_end.isoformat() + "Z"
        )
        previous_analysis = self.analyze_orders(previous_orders)
        
        # 计算变化
        def calc_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 2)
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "current_period": current_analysis,
            "previous_period": previous_analysis,
            "changes": {
                "orders_change_percent": calc_change(
                    current_analysis["total_orders"],
                    previous_analysis["total_orders"]
                ),
                "revenue_change_percent": calc_change(
                    current_analysis["total_amount"],
                    previous_analysis["total_amount"]
                ),
                "aov_change_percent": calc_change(
                    current_analysis["average_order_value"],
                    previous_analysis["average_order_value"]
                ),
            },
            "comparison_hours": current_hours,
        }


class MultiStoreOrdersAnalytics:
    """多店铺订单分析器"""
    
    def __init__(self, clients: Dict[str, SPAPIClient]):
        self.clients = clients
        self.analyzers = {
            store_id: OrdersAnalytics(client)
            for store_id, client in clients.items()
        }
    
    def get_all_stores_metrics(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        获取所有店铺的实时指标
        
        Args:
            time_window_minutes: 时间窗口（分钟）
        
        Returns:
            所有店铺的汇总指标
        """
        all_metrics = []
        
        for store_id, analyzer in self.analyzers.items():
            try:
                marketplace_ids = analyzer.client.credentials.marketplace_ids
                metrics = analyzer.get_order_metrics_realtime(
                    marketplace_ids=marketplace_ids,
                    time_window_minutes=time_window_minutes
                )
                all_metrics.append(metrics)
            except Exception as e:
                logger.error(f"获取店铺 {store_id} 指标失败: {e}")
        
        # 汇总所有店铺数据
        total_orders = sum(m["total_orders"] for m in all_metrics)
        total_revenue = sum(m["total_amount"] for m in all_metrics)
        
        return {
            "total_stores": len(all_metrics),
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "average_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
            "orders_per_hour": sum(m["orders_per_hour"] for m in all_metrics),
            "revenue_per_hour": sum(m["revenue_per_hour"] for m in all_metrics),
            "store_metrics": all_metrics,
            "time_window_minutes": time_window_minutes,
            "analysis_time": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("订单分析模块已加载")