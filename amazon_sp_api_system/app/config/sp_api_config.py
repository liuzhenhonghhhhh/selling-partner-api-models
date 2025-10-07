"""
SP API 配置管理
支持多店铺配置
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import yaml
import os
from enum import Enum


class Region(str, Enum):
    """亚马逊区域枚举"""
    NA = "NA"  # 北美
    EU = "EU"  # 欧洲
    FE = "FE"  # 远东
    SANDBOX = "SANDBOX"  # 沙箱环境


class MarketplaceConfig(BaseModel):
    """市场配置"""
    marketplace_id: str
    country_code: str
    region: Region


# 主要市场配置
MARKETPLACES = {
    "US": MarketplaceConfig(marketplace_id="ATVPDKIKX0DER", country_code="US", region=Region.NA),
    "CA": MarketplaceConfig(marketplace_id="A2EUQ1WTGCTBG2", country_code="CA", region=Region.NA),
    "MX": MarketplaceConfig(marketplace_id="A1AM78C64UM0Y8", country_code="MX", region=Region.NA),
    "UK": MarketplaceConfig(marketplace_id="A1F83G8C2ARO7P", country_code="UK", region=Region.EU),
    "DE": MarketplaceConfig(marketplace_id="A1PA6795UKMFR9", country_code="DE", region=Region.EU),
    "FR": MarketplaceConfig(marketplace_id="A13V1IB3VIYZZH", country_code="FR", region=Region.EU),
    "IT": MarketplaceConfig(marketplace_id="APJ6JRA9NG5V4", country_code="IT", region=Region.EU),
    "ES": MarketplaceConfig(marketplace_id="A1RKKUPIHCS9HS", country_code="ES", region=Region.EU),
    "JP": MarketplaceConfig(marketplace_id="A1VC38T7YXB528", country_code="JP", region=Region.FE),
    "AU": MarketplaceConfig(marketplace_id="A39IBJ37TRP1C6", country_code="AU", region=Region.FE),
    "SG": MarketplaceConfig(marketplace_id="A19VAU5U5O7RUS", country_code="SG", region=Region.FE),
}


class StoreCredentials(BaseModel):
    """单个店铺的凭证配置"""
    store_id: str = Field(..., description="店铺唯一标识")
    store_name: str = Field(..., description="店铺名称")
    client_id: str = Field(..., description="LWA Client ID")
    client_secret: str = Field(..., description="LWA Client Secret")
    refresh_token: str = Field(..., description="刷新令牌")
    region: Region = Field(..., description="区域")
    marketplace_ids: List[str] = Field(default_factory=list, description="市场ID列表")
    aws_access_key: Optional[str] = Field(None, description="AWS访问密钥")
    aws_secret_key: Optional[str] = Field(None, description="AWS密钥")
    role_arn: Optional[str] = Field(None, description="IAM角色ARN")
    enabled: bool = Field(default=True, description="是否启用")


class SPAPIConfig(BaseModel):
    """SP API全局配置"""
    # LWA Token端点
    token_endpoints: Dict[Region, str] = {
        Region.NA: "https://api.amazon.com/auth/o2/token",
        Region.EU: "https://api.amazon.com/auth/o2/token",
        Region.FE: "https://api.amazon.com/auth/o2/token",
        Region.SANDBOX: "https://api.amazon.com/auth/o2/token",
    }
    
    # SP API端点
    api_endpoints: Dict[Region, str] = {
        Region.NA: "https://sellingpartnerapi-na.amazon.com",
        Region.EU: "https://sellingpartnerapi-eu.amazon.com",
        Region.FE: "https://sellingpartnerapi-fe.amazon.com",
        Region.SANDBOX: "https://sandbox.sellingpartnerapi-na.amazon.com",
    }
    
    # 请求限流配置
    rate_limits: Dict[str, Dict[str, float]] = {
        "orders": {"rate": 0.0167, "burst": 20},
        "sales": {"rate": 0.5, "burst": 15},
        "finances": {"rate": 0.5, "burst": 30},
        "reports": {"rate": 0.0222, "burst": 10},
        "products": {"rate": 2, "burst": 10},
        "inventory": {"rate": 2, "burst": 10},
    }
    
    # 缓存配置
    cache_ttl: Dict[str, int] = {
        "orders": 60,  # 订单缓存1分钟
        "sales_metrics": 300,  # 销售指标缓存5分钟
        "finances": 1800,  # 财务数据缓存30分钟
        "inventory": 600,  # 库存缓存10分钟
        "pricing": 300,  # 价格缓存5分钟
    }
    
    # Redis配置
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[str] = Field(default=None)
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///sp_api_analytics.db")
    
    # 日志配置
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/sp_api_analytics.log")


class MultiStoreConfig:
    """多店铺配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv("SP_API_CONFIG", "stores_config.yaml")
        self.stores: Dict[str, StoreCredentials] = {}
        self.global_config = SPAPIConfig()
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载店铺配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
                # 加载全局配置
                if 'global' in config_data:
                    self.global_config = SPAPIConfig(**config_data['global'])
                
                # 加载店铺配置
                if 'stores' in config_data:
                    for store_data in config_data['stores']:
                        store = StoreCredentials(**store_data)
                        self.stores[store.store_id] = store
    
    def add_store(self, store: StoreCredentials):
        """添加店铺配置"""
        self.stores[store.store_id] = store
    
    def get_store(self, store_id: str) -> Optional[StoreCredentials]:
        """获取店铺配置"""
        return self.stores.get(store_id)
    
    def get_all_stores(self) -> List[StoreCredentials]:
        """获取所有启用的店铺"""
        return [store for store in self.stores.values() if store.enabled]
    
    def get_stores_by_region(self, region: Region) -> List[StoreCredentials]:
        """按区域获取店铺"""
        return [store for store in self.stores.values() 
                if store.region == region and store.enabled]
    
    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'global': self.global_config.dict(),
            'stores': [store.dict() for store in self.stores.values()]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)


# 创建示例配置文件的函数
def create_sample_config(filename: str = "stores_config.example.yaml"):
    """创建示例配置文件"""
    sample_config = {
        'global': {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'database_url': 'sqlite:///sp_api_analytics.db',
            'log_level': 'INFO',
        },
        'stores': [
            {
                'store_id': 'store_001',
                'store_name': '美国主店铺',
                'client_id': 'your_client_id_here',
                'client_secret': 'your_client_secret_here',
                'refresh_token': 'your_refresh_token_here',
                'region': 'NA',
                'marketplace_ids': ['ATVPDKIKX0DER'],
                'enabled': True,
            },
            {
                'store_id': 'store_002',
                'store_name': '欧洲店铺',
                'client_id': 'your_client_id_here',
                'client_secret': 'your_client_secret_here',
                'refresh_token': 'your_refresh_token_here',
                'region': 'EU',
                'marketplace_ids': ['A1F83G8C2ARO7P', 'A1PA6795UKMFR9'],
                'enabled': True,
            },
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"示例配置文件已创建: {filename}")


if __name__ == "__main__":
    # 创建示例配置
    create_sample_config()