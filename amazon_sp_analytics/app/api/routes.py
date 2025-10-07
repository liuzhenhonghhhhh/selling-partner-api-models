"""
FastAPI路由定义
提供RESTful API接口供前端调用
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.database import DatabaseManager
from app.services.data_query import DataQueryService
from app.api import schemas

# 创建路由器
api_router = APIRouter()


# 依赖注入：获取数据库会话
def get_db():
    db_manager = get_db_manager()  # 从全局获取
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


# 依赖注入：获取查询服务
def get_query_service(db: Session = Depends(get_db)):
    db_manager = get_db_manager()
    return DataQueryService(db_manager)


# ============= 店铺管理 API =============

@api_router.get("/stores", response_model=List[schemas.StoreInfo])
async def get_stores(
    enabled_only: bool = True,
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取店铺列表"""
    stores = query_service.get_all_stores(enabled_only=enabled_only)
    return stores


@api_router.get("/stores/{store_id}", response_model=schemas.StoreInfo)
async def get_store(
    store_id: str,
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取店铺详情"""
    store = query_service.get_store_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return store


# ============= 实时数据 API =============

@api_router.get("/realtime/overview", response_model=schemas.RealtimeOverview)
async def get_realtime_overview(
    minutes: int = Query(60, ge=1, le=1440),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取实时概览数据"""
    return query_service.get_realtime_overview(minutes=minutes)


@api_router.get("/realtime/stores", response_model=List[schemas.StoreMetrics])
async def get_realtime_stores(
    minutes: int = Query(60, ge=1, le=1440),
    top_n: int = Query(10, ge=1, le=100),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取所有店铺实时数据"""
    return query_service.get_stores_realtime_metrics(minutes=minutes, top_n=top_n)


# ============= 订单数据 API =============

@api_router.get("/orders/summary", response_model=schemas.OrderSummary)
async def get_orders_summary(
    store_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取订单汇总数据"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_orders_summary(
        store_id=store_id,
        start_date=start_date,
        end_date=end_date
    )


@api_router.get("/orders/trend", response_model=List[schemas.OrderTrend])
async def get_orders_trend(
    store_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    granularity: str = Query("day", regex="^(hour|day|week|month)$"),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取订单趋势数据"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_orders_trend(
        store_id=store_id,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity
    )


# ============= 销售数据 API =============

@api_router.get("/sales/summary", response_model=schemas.SalesSummary)
async def get_sales_summary(
    store_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取销售汇总数据"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_sales_summary(
        store_id=store_id,
        start_date=start_date,
        end_date=end_date
    )


@api_router.get("/sales/trend", response_model=List[schemas.SalesTrend])
async def get_sales_trend(
    store_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    granularity: str = Query("day", regex="^(hour|day|week|month)$"),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取销售趋势数据"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_sales_trend(
        store_id=store_id,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity
    )


# ============= 财务数据 API =============

@api_router.get("/finance/summary", response_model=schemas.FinanceSummary)
async def get_finance_summary(
    store_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取财务汇总数据"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_finance_summary(
        store_id=store_id,
        start_date=start_date,
        end_date=end_date
    )


@api_router.get("/finance/profit-trend", response_model=List[schemas.ProfitTrend])
async def get_profit_trend(
    store_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取利润趋势"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_profit_trend(
        store_id=store_id,
        start_date=start_date,
        end_date=end_date
    )


# ============= 排名数据 API =============

@api_router.get("/rankings/stores", response_model=List[schemas.StoreRanking])
async def get_store_rankings(
    metric: str = Query("revenue", regex="^(revenue|orders|profit|margin)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    top_n: int = Query(20, ge=1, le=100),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取店铺排名"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=1)
    if not end_date:
        end_date = datetime.now()
    
    return query_service.get_store_rankings(
        metric=metric,
        start_date=start_date,
        end_date=end_date,
        top_n=top_n
    )


# ============= 告警数据 API =============

@api_router.get("/alerts", response_model=List[schemas.AlertInfo])
async def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取告警列表"""
    return query_service.get_alerts(
        status=status,
        severity=severity,
        limit=limit
    )


@api_router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    query_service: DataQueryService = Depends(get_query_service)
):
    """确认告警"""
    success = query_service.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="告警不存在")
    return {"message": "告警已确认"}


# ============= 监控快照 API =============

@api_router.get("/monitoring/snapshots", response_model=List[schemas.MonitoringSnapshotInfo])
async def get_monitoring_snapshots(
    hours: int = Query(24, ge=1, le=168),
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取监控快照历史"""
    start_time = datetime.now() - timedelta(hours=hours)
    return query_service.get_monitoring_snapshots(start_time=start_time)


# ============= 仪表板数据 API =============

@api_router.get("/dashboard/overview", response_model=schemas.DashboardOverview)
async def get_dashboard_overview(
    query_service: DataQueryService = Depends(get_query_service)
):
    """获取仪表板概览（包含所有关键指标）"""
    return query_service.get_dashboard_overview()


# 全局数据库管理器实例（将由主程序初始化）
_db_manager = None

def init_db_manager(db_manager: DatabaseManager):
    """初始化全局数据库管理器"""
    global _db_manager
    _db_manager = db_manager

def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器"""
    if _db_manager is None:
        raise RuntimeError("数据库管理器未初始化")
    return _db_manager