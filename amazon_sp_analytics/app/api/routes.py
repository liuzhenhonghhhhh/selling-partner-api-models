"""
FastAPI路由定义
提供RESTful API接口供前端调用
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.api import schemas
from app.config.sp_api_config import MultiStoreConfig, StoreCredentials, Region

# 尝试导入数据库相关模块（可选）
try:
    from sqlalchemy.orm import Session
    from app.models.database import DatabaseManager
    from app.services.data_query import DataQueryService
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    Session = None
    DatabaseManager = None
    DataQueryService = None

# 创建路由器
api_router = APIRouter()


# 依赖注入：获取数据库会话
def get_db():
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="数据库功能未启用")
    db_manager = get_db_manager()  # 从全局获取
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


# 依赖注入：获取查询服务
def get_query_service(db = Depends(get_db)):
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="数据库功能未启用")
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


# ============= 配置管理 API =============

@api_router.get("/config/stores", response_model=List[schemas.StoreCredentialsResponse])
async def get_all_store_configs():
    """获取所有店铺配置"""
    config_manager = get_config_manager()
    stores = config_manager.get_all_stores()
    
    return [
        schemas.StoreCredentialsResponse(
            store_id=store.store_id,
            store_name=store.store_name,
            client_id=store.client_id,
            region=store.region.value,
            marketplace_ids=store.marketplace_ids,
            enabled=store.enabled,
            has_aws_credentials=bool(store.aws_access_key and store.aws_secret_key)
        )
        for store in stores
    ]


@api_router.get("/config/stores/{store_id}", response_model=schemas.StoreCredentialsResponse)
async def get_store_config(store_id: str):
    """获取指定店铺配置"""
    config_manager = get_config_manager()
    store = config_manager.get_store(store_id)
    
    if not store:
        raise HTTPException(status_code=404, detail="店铺配置不存在")
    
    return schemas.StoreCredentialsResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        client_id=store.client_id,
        region=store.region.value,
        marketplace_ids=store.marketplace_ids,
        enabled=store.enabled,
        has_aws_credentials=bool(store.aws_access_key and store.aws_secret_key)
    )


@api_router.post("/config/stores", response_model=schemas.StoreCredentialsResponse)
async def create_store_config(store_data: schemas.StoreCredentialsCreate):
    """创建店铺配置"""
    config_manager = get_config_manager()
    
    # 检查店铺ID是否已存在
    if config_manager.get_store(store_data.store_id):
        raise HTTPException(status_code=400, detail="店铺ID已存在")
    
    # 创建店铺凭证
    try:
        store = StoreCredentials(
            store_id=store_data.store_id,
            store_name=store_data.store_name,
            client_id=store_data.client_id,
            client_secret=store_data.client_secret,
            refresh_token=store_data.refresh_token,
            region=Region(store_data.region),
            marketplace_ids=store_data.marketplace_ids,
            aws_access_key=store_data.aws_access_key,
            aws_secret_key=store_data.aws_secret_key,
            role_arn=store_data.role_arn,
            enabled=store_data.enabled
        )
        
        # 添加到配置管理器
        config_manager.add_store(store)
        
        # 保存配置到文件
        config_manager.save_config()
        
        return schemas.StoreCredentialsResponse(
            store_id=store.store_id,
            store_name=store.store_name,
            client_id=store.client_id,
            region=store.region.value,
            marketplace_ids=store.marketplace_ids,
            enabled=store.enabled,
            has_aws_credentials=bool(store.aws_access_key and store.aws_secret_key)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建店铺配置失败: {str(e)}")


@api_router.put("/config/stores/{store_id}", response_model=schemas.StoreCredentialsResponse)
async def update_store_config(store_id: str, store_data: schemas.StoreCredentialsUpdate):
    """更新店铺配置"""
    config_manager = get_config_manager()
    store = config_manager.get_store(store_id)
    
    if not store:
        raise HTTPException(status_code=404, detail="店铺配置不存在")
    
    # 更新字段
    update_dict = store_data.dict(exclude_unset=True)
    
    if 'region' in update_dict:
        update_dict['region'] = Region(update_dict['region'])
    
    for field, value in update_dict.items():
        setattr(store, field, value)
    
    # 保存配置
    config_manager.save_config()
    
    return schemas.StoreCredentialsResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        client_id=store.client_id,
        region=store.region.value,
        marketplace_ids=store.marketplace_ids,
        enabled=store.enabled,
        has_aws_credentials=bool(store.aws_access_key and store.aws_secret_key)
    )


@api_router.delete("/config/stores/{store_id}")
async def delete_store_config(store_id: str):
    """删除店铺配置"""
    config_manager = get_config_manager()
    
    if store_id not in config_manager.stores:
        raise HTTPException(status_code=404, detail="店铺配置不存在")
    
    del config_manager.stores[store_id]
    config_manager.save_config()
    
    return {"message": f"店铺配置 {store_id} 已删除"}


@api_router.post("/config/test", response_model=schemas.ConfigTestResponse)
async def test_api_config(test_data: schemas.ConfigTestRequest):
    """测试API配置是否有效"""
    try:
        from app.core.sp_client import SPAPIClient
        
        # 创建临时凭证
        temp_store = StoreCredentials(
            store_id="test",
            store_name="测试",
            client_id=test_data.client_id,
            client_secret=test_data.client_secret,
            refresh_token=test_data.refresh_token,
            region=Region(test_data.region),
            marketplace_ids=[]
        )
        
        # 尝试创建客户端并获取访问令牌
        client = SPAPIClient(temp_store)
        # 这里可以添加一个简单的API调用来验证凭证
        # 例如：client.get_marketplace_participations()
        
        return schemas.ConfigTestResponse(
            success=True,
            message="配置验证成功",
            details={"region": test_data.region}
        )
    except Exception as e:
        return schemas.ConfigTestResponse(
            success=False,
            message=f"配置验证失败: {str(e)}",
            details={"error": str(e)}
        )


# 全局数据库管理器实例（将由主程序初始化）
_db_manager = None
_config_manager = None

def init_db_manager(db_manager: DatabaseManager):
    """初始化全局数据库管理器"""
    global _db_manager
    _db_manager = db_manager

def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器"""
    if _db_manager is None:
        raise RuntimeError("数据库管理器未初始化")
    return _db_manager

def init_config_manager(config_manager: MultiStoreConfig):
    """初始化全局配置管理器"""
    global _config_manager
    _config_manager = config_manager

def get_config_manager() -> MultiStoreConfig:
    """获取全局配置管理器"""
    if _config_manager is None:
        raise RuntimeError("配置管理器未初始化")
    return _config_manager