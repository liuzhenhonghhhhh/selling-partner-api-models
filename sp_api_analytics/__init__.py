"""
亚马逊SP API多店铺销售分析系统
支持100+店铺实时数据监控和分析
"""

__version__ = "1.0.0"
__author__ = "SP API Analytics Team"

from .config import SPAPIConfig, StoreCredentials, MultiStoreConfig, Region, MARKETPLACES
from .core import SPAPIClient, MultiStoreClient
from .analytics import (
    OrdersAnalytics,
    MultiStoreOrdersAnalytics,
    SalesAnalytics,
    MultiStoreSalesAnalytics,
    FinanceAnalytics,
    MultiStoreFinanceAnalytics,
)
from .cache import RedisCache, init_cache, get_cache
from .utils import RealtimeMonitor, DashboardData

__all__ = [
    # 配置
    'SPAPIConfig',
    'StoreCredentials',
    'MultiStoreConfig',
    'Region',
    'MARKETPLACES',
    
    # 客户端
    'SPAPIClient',
    'MultiStoreClient',
    
    # 分析模块
    'OrdersAnalytics',
    'MultiStoreOrdersAnalytics',
    'SalesAnalytics',
    'MultiStoreSalesAnalytics',
    'FinanceAnalytics',
    'MultiStoreFinanceAnalytics',
    
    # 缓存
    'RedisCache',
    'init_cache',
    'get_cache',
    
    # 监控
    'RealtimeMonitor',
    'DashboardData',
]