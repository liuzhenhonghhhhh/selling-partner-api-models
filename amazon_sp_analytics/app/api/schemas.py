"""
API数据模型（Pydantic schemas）
定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============= 店铺相关 =============

class StoreInfo(BaseModel):
    """店铺信息"""
    store_id: str
    store_name: str
    region: str
    marketplace_ids: List[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= 实时数据 =============

class RealtimeOverview(BaseModel):
    """实时概览"""
    total_stores: int
    total_orders_1h: int
    total_revenue_1h: float
    orders_per_hour: float
    revenue_per_hour: float
    average_order_value: float
    timestamp: datetime


class StoreMetrics(BaseModel):
    """店铺指标"""
    store_id: str
    store_name: str
    orders: int
    revenue: float
    average_order_value: float
    orders_per_hour: float


# ============= 订单数据 =============

class OrderSummary(BaseModel):
    """订单汇总"""
    total_orders: int
    total_amount: float
    average_order_value: float
    orders_by_status: Dict[str, int]
    orders_by_channel: Dict[str, int]
    afn_percentage: float
    mfn_percentage: float


class OrderTrend(BaseModel):
    """订单趋势"""
    date: datetime
    orders: int
    revenue: float
    average_order_value: float


# ============= 销售数据 =============

class SalesSummary(BaseModel):
    """销售汇总"""
    total_orders: int
    total_units: int
    total_sales: float
    average_order_value: float
    average_units_per_order: float
    currency: str = "USD"


class SalesTrend(BaseModel):
    """销售趋势"""
    date: datetime
    orders: int
    units: int
    sales: float


# ============= 财务数据 =============

class FinanceSummary(BaseModel):
    """财务汇总"""
    total_revenue: float
    total_fees: float
    total_refunds: float
    net_profit: float
    profit_margin: float
    revenue_breakdown: Dict[str, float]
    fee_breakdown: Dict[str, float]


class ProfitTrend(BaseModel):
    """利润趋势"""
    date: datetime
    revenue: float
    fees: float
    profit: float
    margin: float


# ============= 排名数据 =============

class StoreRanking(BaseModel):
    """店铺排名"""
    rank: int
    store_id: str
    store_name: str
    value: float
    percentage: float


# ============= 告警数据 =============

class AlertInfo(BaseModel):
    """告警信息"""
    id: int
    alert_time: datetime
    alert_type: str
    severity: str
    message: str
    value: Optional[float]
    threshold: Optional[float]
    store_id: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


# ============= 监控快照 =============

class MonitoringSnapshotInfo(BaseModel):
    """监控快照"""
    snapshot_time: datetime
    total_stores: int
    total_orders_1h: int
    total_revenue_1h: float
    orders_per_hour: float
    average_profit_margin: float
    
    class Config:
        from_attributes = True


# ============= 仪表板 =============

class DashboardOverview(BaseModel):
    """仪表板概览"""
    # 实时指标
    realtime: RealtimeOverview
    
    # 24小时数据
    last_24h: Dict[str, Any]
    
    # 7天数据
    last_7d: Dict[str, Any]
    
    # 店铺排名
    top_stores: List[StoreRanking]
    
    # 最近告警
    recent_alerts: List[AlertInfo]
    
    # 趋势图数据
    order_trend: List[OrderTrend]
    sales_trend: List[SalesTrend]
    profit_trend: List[ProfitTrend]