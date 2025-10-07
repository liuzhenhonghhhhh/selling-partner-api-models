"""
SP API 客户端核心模块
支持LWA认证、请求签名、限流等
"""
import time
import hashlib
import hmac
import requests
import backoff
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import quote
from loguru import logger
from config.sp_api_config import StoreCredentials, SPAPIConfig, Region


class LWAClient:
    """Login with Amazon (LWA) 认证客户端"""
    
    def __init__(self, credentials: StoreCredentials, config: SPAPIConfig):
        self.credentials = credentials
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    def get_access_token(self) -> str:
        """获取访问令牌（带自动刷新）"""
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry - timedelta(minutes=5):
                return self.access_token
        
        # 刷新令牌
        self._refresh_access_token()
        return self.access_token
    
    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_time=30
    )
    def _refresh_access_token(self):
        """刷新访问令牌"""
        token_url = self.config.token_endpoints[self.credentials.region]
        
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.credentials.refresh_token,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
        }
        
        logger.info(f"刷新店铺 {self.credentials.store_name} 的访问令牌")
        
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        expires_in = token_data.get('expires_in', 3600)
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
        
        logger.success(f"访问令牌刷新成功，有效期至: {self.token_expiry}")


class RateLimiter:
    """API请求限流器"""
    
    def __init__(self, rate: float, burst: int):
        """
        Args:
            rate: 每秒请求数
            burst: 突发请求数
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
    
    def acquire(self):
        """获取请求令牌（阻塞直到可用）"""
        while True:
            now = time.time()
            elapsed = now - self.last_update
            
            # 补充令牌
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            # 等待时间
            sleep_time = (1 - self.tokens) / self.rate
            time.sleep(sleep_time)


class SPAPIClient:
    """SP API 主客户端"""
    
    def __init__(self, credentials: StoreCredentials, config: SPAPIConfig):
        self.credentials = credentials
        self.config = config
        self.lwa_client = LWAClient(credentials, config)
        self.base_url = config.api_endpoints[credentials.region]
        
        # 初始化限流器
        self.rate_limiters: Dict[str, RateLimiter] = {}
        for api_name, limits in config.rate_limits.items():
            self.rate_limiters[api_name] = RateLimiter(
                rate=limits['rate'],
                burst=int(limits['burst'])
            )
    
    def _get_rate_limiter(self, endpoint: str) -> RateLimiter:
        """根据endpoint获取对应的限流器"""
        if 'orders' in endpoint:
            return self.rate_limiters.get('orders')
        elif 'sales' in endpoint:
            return self.rate_limiters.get('sales')
        elif 'finances' in endpoint:
            return self.rate_limiters.get('finances')
        elif 'reports' in endpoint:
            return self.rate_limiters.get('reports')
        elif 'fba/inventory' in endpoint:
            return self.rate_limiters.get('inventory')
        else:
            return self.rate_limiters.get('orders')  # 默认使用订单限流
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, requests.exceptions.HTTPError),
        max_tries=5,
        giveup=lambda e: e.response.status_code < 500 if hasattr(e, 'response') else False
    )
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        发送SP API请求
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点路径
            params: 查询参数
            data: 请求体数据
            headers: 额外的请求头
        
        Returns:
            API响应的JSON数据
        """
        # 限流
        rate_limiter = self._get_rate_limiter(endpoint)
        if rate_limiter:
            rate_limiter.acquire()
        
        # 获取访问令牌
        access_token = self.lwa_client.get_access_token()
        
        # 构建完整URL
        url = f"{self.base_url}{endpoint}"
        
        # 构建请求头
        request_headers = {
            'x-amz-access-token': access_token,
            'Content-Type': 'application/json',
        }
        if headers:
            request_headers.update(headers)
        
        # 记录请求
        logger.debug(f"[{self.credentials.store_name}] {method} {url}")
        logger.debug(f"参数: {params}")
        
        # 发送请求
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=request_headers,
            timeout=30
        )
        
        # 检查响应
        if response.status_code == 429:
            logger.warning("遇到限流，等待重试...")
            time.sleep(5)
            raise requests.exceptions.HTTPError(response=response)
        
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"响应: {result}")
        
        return result
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """GET请求"""
        return self.request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """POST请求"""
        return self.request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """PUT请求"""
        return self.request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict:
        """DELETE请求"""
        return self.request('DELETE', endpoint, **kwargs)


class MultiStoreClient:
    """多店铺客户端管理器"""
    
    def __init__(self, config: SPAPIConfig):
        self.config = config
        self.clients: Dict[str, SPAPIClient] = {}
    
    def add_store(self, credentials: StoreCredentials) -> SPAPIClient:
        """添加店铺并创建客户端"""
        client = SPAPIClient(credentials, self.config)
        self.clients[credentials.store_id] = client
        logger.info(f"已添加店铺: {credentials.store_name} ({credentials.store_id})")
        return client
    
    def get_client(self, store_id: str) -> Optional[SPAPIClient]:
        """获取指定店铺的客户端"""
        return self.clients.get(store_id)
    
    def get_all_clients(self) -> Dict[str, SPAPIClient]:
        """获取所有店铺客户端"""
        return self.clients
    
    def remove_store(self, store_id: str):
        """移除店铺"""
        if store_id in self.clients:
            del self.clients[store_id]
            logger.info(f"已移除店铺: {store_id}")


if __name__ == "__main__":
    # 测试示例
    from config.sp_api_config import Region
    
    # 创建测试凭证
    credentials = StoreCredentials(
        store_id="test_store",
        store_name="测试店铺",
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        region=Region.NA,
        marketplace_ids=["ATVPDKIKX0DER"]
    )
    
    config = SPAPIConfig()
    client = SPAPIClient(credentials, config)
    
    print("SP API 客户端初始化成功")