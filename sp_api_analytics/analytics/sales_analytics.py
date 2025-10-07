"""
销售数据分析模块
支持销售指标统计、趋势分析
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

from core.sp_client import SPAPIClient


class SalesAnalytics:
    """销售数据分析器"""
    
    def __init__(self, client: SPAPIClient):
        self.client = client
        self.store_id = client.credentials.store_id
        self.store_name = client.credentials.store_name
    
    def get_order_metrics(
        self,
        marketplace_ids: List[str],
        interval: str,
        granularity: str = "Hour",
        granularity_timezone: str = "UTC",
        buyer_type: str = "All",
        fulfillment_network: Optional[str] = None,
        first_day_of_week: str = "Monday",
        asin: Optional[str] = None,
        sku: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取销售指标数据
        
        Args:
            marketplace_ids: 市场ID列表
            interval: 时间区间 (格式: "2024-01-01T00:00:00Z--2024-01-02T00:00:00Z")
            granularity: 粒度 (Hour, Day, Week, Month, Year, Total)
            granularity_timezone: 时区
            buyer_type: 买家类型 (All, B2B, B2C)
            fulfillment_network: 配送网络 (Amazon, Seller)
            first_day_of_week: 一周的第一天
            asin: ASIN筛选
            sku: SKU筛选
        
        Returns:
            销售指标数据
        """
        endpoint = "/sales/v1/orderMetrics"
        
        params = {
            "marketplaceIds": ",".join(marketplace_ids),
            "interval": interval,
            "granularity": granularity,
        }
        
        if granularity != "Hour":
            params["granularityTimeZone"] = granularity_timezone
        
        if buyer_type:
            params["buyerType"] = buyer_type
        if fulfillment_network:
            params["fulfillmentNetwork"] = fulfillment_network
        if first_day_of_week:
            params["firstDayOfWeek"] = first_day_of_week
        if asin:
            params["asin"] = asin
        if sku:
            params["sku"] = sku
        
        try:
            logger.info(f"[{self.store_name}] 获取销售指标数据...")
            response = self.client.get(endpoint, params=params)
            
            if "payload" in response:
                logger.success(f"[{self.store_name}] 销售指标数据获取成功")
                return response["payload"]
        except Exception as e:
            logger.error(f"[{self.store_name}] 获取销售指标失败: {e}")
        
        return {}
    
    def get_sales_by_hour(
        self,
        marketplace_ids: List[str],
        start_time: datetime,
        end_time: datetime,
        timezone: str = "UTC"
    ) -> List[Dict[str, Any]]:
        """
        按小时获取销售数据（适用于实时监控）
        
        Args:
            marketplace_ids: 市场ID列表
            start_time: 开始时间
            end_time: 结束时间
            timezone: 时区
        
        Returns:
            按小时聚合的销售数据
        """
        interval = f"{start_time.isoformat()}--{end_time.isoformat()}"
        
        metrics = self.get_order_metrics(
            marketplace_ids=marketplace_ids,
            interval=interval,
            granularity="Hour",
            granularity_timezone=timezone
        )
        
        return metrics.get("orderMetrics", [])
    
    def get_sales_by_day(
        self,
        marketplace_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        timezone: str = "UTC"
    ) -> List[Dict[str, Any]]:
        """
        按天获取销售数据
        
        Args:
            marketplace_ids: 市场ID列表
            start_date: 开始日期
            end_date: 结束日期
            timezone: 时区
        
        Returns:
            按天聚合的销售数据
        """
        interval = f"{start_date.isoformat()}--{end_date.isoformat()}"
        
        metrics = self.get_order_metrics(
            marketplace_ids=marketplace_ids,
            interval=interval,
            granularity="Day",
            granularity_timezone=timezone
        )
        
        return metrics.get("orderMetrics", [])
    
    def analyze_sales_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析销售指标数据
        
        Args:
            metrics: 销售指标列表
        
        Returns:
            分析结果
        """
        if not metrics:
            return {
                "total_orders": 0,
                "total_units": 0,
                "total_sales": 0,
                "average_order_value": 0,
                "average_units_per_order": 0,
            }
        
        total_orders = 0
        total_units = 0
        total_sales = 0
        
        for metric in metrics:
            total_orders += metric.get("orderCount", 0)
            total_units += metric.get("unitCount", 0)
            
            # 处理销售额
            if "orderItemCount" in metric:
                total_sales += metric.get("totalSales", {}).get("amount", 0)
        
        average_order_value = total_sales / total_orders if total_orders > 0 else 0
        average_units_per_order = total_units / total_orders if total_orders > 0 else 0
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "total_orders": total_orders,
            "total_units": total_units,
            "total_sales": round(total_sales, 2),
            "average_order_value": round(average_order_value, 2),
            "average_units_per_order": round(average_units_per_order, 2),
            "currency": metrics[0].get("totalSales", {}).get("currencyCode", "USD") if metrics else "USD",
            "data_points": len(metrics),
            "analysis_time": datetime.now().isoformat(),
        }
    
    def get_realtime_sales_dashboard(
        self,
        marketplace_ids: List[str],
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        获取实时销售仪表板数据
        
        Args:
            marketplace_ids: 市场ID列表
            hours: 小时数
        
        Returns:
            实时销售仪表板数据
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 按小时获取数据
        hourly_metrics = self.get_sales_by_hour(
            marketplace_ids=marketplace_ids,
            start_time=start_time,
            end_time=end_time
        )
        
        # 分析数据
        analysis = self.analyze_sales_metrics(hourly_metrics)
        
        # 添加时间序列数据
        time_series = []
        for metric in hourly_metrics:
            time_series.append({
                "interval": metric.get("interval"),
                "orders": metric.get("orderCount", 0),
                "units": metric.get("unitCount", 0),
                "sales": metric.get("totalSales", {}).get("amount", 0),
            })
        
        analysis["time_series"] = time_series
        analysis["hours"] = hours
        
        return analysis
    
    def calculate_growth_rate(
        self,
        marketplace_ids: List[str],
        current_days: int = 7,
        comparison_days: int = 7
    ) -> Dict[str, Any]:
        """
        计算增长率
        
        Args:
            marketplace_ids: 市场ID列表
            current_days: 当前周期天数
            comparison_days: 对比周期天数
        
        Returns:
            增长率分析
        """
        # 当前周期
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=current_days)
        current_metrics = self.get_sales_by_day(
            marketplace_ids=marketplace_ids,
            start_date=current_start,
            end_date=current_end
        )
        current_analysis = self.analyze_sales_metrics(current_metrics)
        
        # 对比周期
        comparison_end = current_start
        comparison_start = comparison_end - timedelta(days=comparison_days)
        comparison_metrics = self.get_sales_by_day(
            marketplace_ids=marketplace_ids,
            start_date=comparison_start,
            end_date=comparison_end
        )
        comparison_analysis = self.analyze_sales_metrics(comparison_metrics)
        
        # 计算增长率
        def calc_growth(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 2)
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "current_period": current_analysis,
            "comparison_period": comparison_analysis,
            "growth_rates": {
                "orders_growth": calc_growth(
                    current_analysis["total_orders"],
                    comparison_analysis["total_orders"]
                ),
                "sales_growth": calc_growth(
                    current_analysis["total_sales"],
                    comparison_analysis["total_sales"]
                ),
                "units_growth": calc_growth(
                    current_analysis["total_units"],
                    comparison_analysis["total_units"]
                ),
                "aov_growth": calc_growth(
                    current_analysis["average_order_value"],
                    comparison_analysis["average_order_value"]
                ),
            },
        }


class MultiStoreSalesAnalytics:
    """多店铺销售分析器"""
    
    def __init__(self, clients: Dict[str, SPAPIClient]):
        self.clients = clients
        self.analyzers = {
            store_id: SalesAnalytics(client)
            for store_id, client in clients.items()
        }
    
    def get_all_stores_sales_dashboard(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取所有店铺的销售仪表板
        
        Args:
            hours: 小时数
        
        Returns:
            所有店铺的销售数据汇总
        """
        all_dashboards = []
        
        for store_id, analyzer in self.analyzers.items():
            try:
                marketplace_ids = analyzer.client.credentials.marketplace_ids
                dashboard = analyzer.get_realtime_sales_dashboard(
                    marketplace_ids=marketplace_ids,
                    hours=hours
                )
                all_dashboards.append(dashboard)
            except Exception as e:
                logger.error(f"获取店铺 {store_id} 销售数据失败: {e}")
        
        # 汇总数据
        total_orders = sum(d["total_orders"] for d in all_dashboards)
        total_units = sum(d["total_units"] for d in all_dashboards)
        total_sales = sum(d["total_sales"] for d in all_dashboards)
        
        return {
            "total_stores": len(all_dashboards),
            "total_orders": total_orders,
            "total_units": total_units,
            "total_sales": round(total_sales, 2),
            "average_order_value": round(total_sales / total_orders, 2) if total_orders > 0 else 0,
            "average_units_per_order": round(total_units / total_orders, 2) if total_orders > 0 else 0,
            "store_dashboards": all_dashboards,
            "hours": hours,
            "analysis_time": datetime.now().isoformat(),
        }
    
    def get_top_performing_stores(
        self,
        hours: int = 24,
        metric: str = "total_sales",
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取表现最好的店铺
        
        Args:
            hours: 小时数
            metric: 排序指标 (total_sales, total_orders, total_units)
            top_n: 返回前N个
        
        Returns:
            排名前N的店铺
        """
        all_dashboards = []
        
        for store_id, analyzer in self.analyzers.items():
            try:
                marketplace_ids = analyzer.client.credentials.marketplace_ids
                dashboard = analyzer.get_realtime_sales_dashboard(
                    marketplace_ids=marketplace_ids,
                    hours=hours
                )
                all_dashboards.append(dashboard)
            except Exception as e:
                logger.error(f"获取店铺 {store_id} 销售数据失败: {e}")
        
        # 排序
        sorted_stores = sorted(
            all_dashboards,
            key=lambda x: x.get(metric, 0),
            reverse=True
        )
        
        return sorted_stores[:top_n]


if __name__ == "__main__":
    print("销售分析模块已加载")