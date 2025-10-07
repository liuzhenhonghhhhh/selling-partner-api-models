"""
实时监控模块
支持多店铺实时数据监控、告警
"""
import time
import threading
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from core.sp_client import MultiStoreClient
from analytics.orders_analytics import MultiStoreOrdersAnalytics
from analytics.sales_analytics import MultiStoreSalesAnalytics
from analytics.finance_analytics import MultiStoreFinanceAnalytics


class MetricsSnapshot:
    """指标快照"""
    
    def __init__(self, metrics: Dict[str, Any]):
        self.metrics = metrics
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"MetricsSnapshot(timestamp={self.timestamp}, metrics={self.metrics})"


class RealtimeMonitor:
    """实时监控器"""
    
    def __init__(
        self,
        multi_store_client: MultiStoreClient,
        update_interval: int = 60,  # 更新间隔（秒）
    ):
        self.multi_store_client = multi_store_client
        self.update_interval = update_interval
        
        # 初始化分析器
        clients = multi_store_client.get_all_clients()
        self.orders_analytics = MultiStoreOrdersAnalytics(clients)
        self.sales_analytics = MultiStoreSalesAnalytics(clients)
        self.finance_analytics = MultiStoreFinanceAnalytics(clients)
        
        # 监控状态
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # 指标历史
        self.metrics_history: List[MetricsSnapshot] = []
        self.max_history_size = 1000
        
        # 告警回调
        self.alert_callbacks: List[Callable] = []
        
        # 告警阈值
        self.alert_thresholds = {
            "min_orders_per_hour": 0,  # 最小订单/小时
            "max_order_value": 100000,  # 最大订单金额
            "min_profit_margin": 0,  # 最小利润率
        }
    
    def set_alert_threshold(self, metric: str, value: float):
        """设置告警阈值"""
        self.alert_thresholds[metric] = value
        logger.info(f"设置告警阈值: {metric} = {value}")
    
    def add_alert_callback(self, callback: Callable):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """采集指标数据"""
        try:
            # 订单指标（最近1小时）
            orders_metrics = self.orders_analytics.get_all_stores_metrics(
                time_window_minutes=60
            )
            
            # 销售指标（最近24小时）
            sales_metrics = self.sales_analytics.get_all_stores_sales_dashboard(
                hours=24
            )
            
            # 财务指标（最近7天）
            finance_metrics = self.finance_analytics.get_all_stores_profit_summary(
                days=7
            )
            
            return {
                "orders": orders_metrics,
                "sales": sales_metrics,
                "finance": finance_metrics,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"采集指标失败: {e}")
            return {}
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """检查告警条件"""
        alerts = []
        
        # 检查订单量
        if metrics.get("orders"):
            orders_per_hour = metrics["orders"].get("orders_per_hour", 0)
            min_threshold = self.alert_thresholds.get("min_orders_per_hour", 0)
            
            if orders_per_hour < min_threshold:
                alerts.append({
                    "type": "low_orders",
                    "severity": "warning",
                    "message": f"订单量过低: {orders_per_hour:.2f}/小时 (阈值: {min_threshold})",
                    "value": orders_per_hour,
                    "threshold": min_threshold,
                })
        
        # 检查利润率
        if metrics.get("finance"):
            profit_margin = metrics["finance"].get("average_profit_margin", 0)
            min_margin = self.alert_thresholds.get("min_profit_margin", 0)
            
            if profit_margin < min_margin:
                alerts.append({
                    "type": "low_profit_margin",
                    "severity": "critical",
                    "message": f"利润率过低: {profit_margin:.2f}% (阈值: {min_margin}%)",
                    "value": profit_margin,
                    "threshold": min_margin,
                })
        
        # 触发告警回调
        if alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alerts)
                except Exception as e:
                    logger.error(f"执行告警回调失败: {e}")
        
        return alerts
    
    def _monitor_loop(self):
        """监控循环"""
        logger.info("实时监控已启动")
        
        while self.is_running:
            try:
                # 采集指标
                logger.info("采集指标数据...")
                metrics = self._collect_metrics()
                
                if metrics:
                    # 保存快照
                    snapshot = MetricsSnapshot(metrics)
                    self.metrics_history.append(snapshot)
                    
                    # 限制历史大小
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history = self.metrics_history[-self.max_history_size:]
                    
                    # 检查告警
                    alerts = self._check_alerts(metrics)
                    if alerts:
                        logger.warning(f"触发 {len(alerts)} 个告警")
                    
                    logger.success("指标采集完成")
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
            
            # 等待下一次更新
            time.sleep(self.update_interval)
        
        logger.info("实时监控已停止")
    
    def start(self):
        """启动监控"""
        if self.is_running:
            logger.warning("监控已在运行")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.success(f"监控已启动，更新间隔: {self.update_interval}秒")
    
    def stop(self):
        """停止监控"""
        if not self.is_running:
            logger.warning("监控未在运行")
            return
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("监控已停止")
    
    def get_latest_metrics(self) -> Optional[MetricsSnapshot]:
        """获取最新指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, minutes: int = 60) -> List[MetricsSnapshot]:
        """
        获取历史指标
        
        Args:
            minutes: 最近N分钟的数据
        
        Returns:
            指标快照列表
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            snapshot for snapshot in self.metrics_history
            if snapshot.timestamp >= cutoff_time
        ]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        latest = self.get_latest_metrics()
        
        if not latest:
            return {
                "status": "no_data",
                "message": "暂无监控数据",
            }
        
        metrics = latest.metrics
        
        return {
            "status": "active",
            "last_update": latest.timestamp.isoformat(),
            "total_stores": metrics.get("orders", {}).get("total_stores", 0),
            "total_orders_1h": metrics.get("orders", {}).get("total_orders", 0),
            "total_revenue_24h": metrics.get("sales", {}).get("total_sales", 0),
            "total_profit_7d": metrics.get("finance", {}).get("total_profit", 0),
            "orders_per_hour": metrics.get("orders", {}).get("orders_per_hour", 0),
            "average_profit_margin": metrics.get("finance", {}).get("average_profit_margin", 0),
            "history_points": len(self.metrics_history),
        }


class DashboardData:
    """仪表板数据聚合器"""
    
    def __init__(self, monitor: RealtimeMonitor):
        self.monitor = monitor
    
    def get_overview_dashboard(self) -> Dict[str, Any]:
        """获取概览仪表板"""
        latest = self.monitor.get_latest_metrics()
        
        if not latest:
            return {"error": "暂无数据"}
        
        metrics = latest.metrics
        
        return {
            "timestamp": latest.timestamp.isoformat(),
            "overview": {
                "total_stores": metrics.get("orders", {}).get("total_stores", 0),
                "orders_per_hour": metrics.get("orders", {}).get("orders_per_hour", 0),
                "revenue_per_hour": metrics.get("orders", {}).get("revenue_per_hour", 0),
                "total_revenue_24h": metrics.get("sales", {}).get("total_sales", 0),
                "total_profit_7d": metrics.get("finance", {}).get("total_profit", 0),
                "profit_margin": metrics.get("finance", {}).get("average_profit_margin", 0),
            },
            "orders": {
                "total_1h": metrics.get("orders", {}).get("total_orders", 0),
                "total_revenue_1h": metrics.get("orders", {}).get("total_revenue", 0),
                "average_order_value": metrics.get("orders", {}).get("average_order_value", 0),
            },
            "sales_24h": {
                "total_orders": metrics.get("sales", {}).get("total_orders", 0),
                "total_units": metrics.get("sales", {}).get("total_units", 0),
                "total_sales": metrics.get("sales", {}).get("total_sales", 0),
            },
            "finance_7d": {
                "revenue": metrics.get("finance", {}).get("total_revenue", 0),
                "fees": metrics.get("finance", {}).get("total_fees", 0),
                "refunds": metrics.get("finance", {}).get("total_refunds", 0),
                "profit": metrics.get("finance", {}).get("total_profit", 0),
            },
        }
    
    def get_store_rankings(self) -> Dict[str, Any]:
        """获取店铺排名"""
        latest = self.monitor.get_latest_metrics()
        
        if not latest or "orders" not in latest.metrics:
            return {"error": "暂无数据"}
        
        store_metrics = latest.metrics["orders"].get("store_metrics", [])
        
        # 按订单量排序
        by_orders = sorted(
            store_metrics,
            key=lambda x: x.get("total_orders", 0),
            reverse=True
        )
        
        # 按收入排序
        by_revenue = sorted(
            store_metrics,
            key=lambda x: x.get("total_amount", 0),
            reverse=True
        )
        
        return {
            "timestamp": latest.timestamp.isoformat(),
            "by_orders": [
                {
                    "store_id": s.get("store_id"),
                    "store_name": s.get("store_name"),
                    "orders": s.get("total_orders", 0),
                }
                for s in by_orders[:10]
            ],
            "by_revenue": [
                {
                    "store_id": s.get("store_id"),
                    "store_name": s.get("store_name"),
                    "revenue": s.get("total_amount", 0),
                }
                for s in by_revenue[:10]
            ],
        }


if __name__ == "__main__":
    print("实时监控模块已加载")