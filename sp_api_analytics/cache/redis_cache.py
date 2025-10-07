"""
Redis缓存管理模块
支持数据缓存、过期策略
"""
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis模块未安装，缓存功能将被禁用")


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True
    ):
        if not REDIS_AVAILABLE:
            logger.warning("Redis不可用，缓存将使用内存字典")
            self.client = None
            self._memory_cache = {}
            return
        
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=5
            )
            # 测试连接
            self.client.ping()
            logger.success(f"Redis连接成功: {host}:{port}")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.client = None
            self._memory_cache = {}
    
    def _make_key(self, namespace: str, key: str) -> str:
        """生成缓存键"""
        return f"spapi:{namespace}:{key}"
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            namespace: 命名空间
            key: 键
        
        Returns:
            缓存的数据，不存在则返回None
        """
        cache_key = self._make_key(namespace, key)
        
        if self.client is None:
            # 使用内存缓存
            return self._memory_cache.get(cache_key)
        
        try:
            data = self.client.get(cache_key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"获取缓存失败 {cache_key}: {e}")
        
        return None
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存数据
        
        Args:
            namespace: 命名空间
            key: 键
            value: 值
            ttl: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        cache_key = self._make_key(namespace, key)
        
        try:
            data = json.dumps(value, ensure_ascii=False)
            
            if self.client is None:
                # 使用内存缓存（不支持TTL）
                self._memory_cache[cache_key] = value
                return True
            
            if ttl:
                self.client.setex(cache_key, ttl, data)
            else:
                self.client.set(cache_key, data)
            
            return True
        except Exception as e:
            logger.error(f"设置缓存失败 {cache_key}: {e}")
            return False
    
    def delete(self, namespace: str, key: str) -> bool:
        """
        删除缓存数据
        
        Args:
            namespace: 命名空间
            key: 键
        
        Returns:
            是否删除成功
        """
        cache_key = self._make_key(namespace, key)
        
        if self.client is None:
            self._memory_cache.pop(cache_key, None)
            return True
        
        try:
            self.client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 {cache_key}: {e}")
            return False
    
    def clear_namespace(self, namespace: str) -> bool:
        """
        清空命名空间下的所有缓存
        
        Args:
            namespace: 命名空间
        
        Returns:
            是否清空成功
        """
        if self.client is None:
            # 清空内存缓存中的对应命名空间
            prefix = f"spapi:{namespace}:"
            keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._memory_cache[k]
            return True
        
        try:
            pattern = f"spapi:{namespace}:*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            logger.info(f"清空命名空间 {namespace} 的 {len(keys)} 个缓存")
            return True
        except Exception as e:
            logger.error(f"清空命名空间缓存失败 {namespace}: {e}")
            return False
    
    def exists(self, namespace: str, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            namespace: 命名空间
            key: 键
        
        Returns:
            是否存在
        """
        cache_key = self._make_key(namespace, key)
        
        if self.client is None:
            return cache_key in self._memory_cache
        
        try:
            return self.client.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"检查缓存失败 {cache_key}: {e}")
            return False
    
    def get_ttl(self, namespace: str, key: str) -> Optional[int]:
        """
        获取缓存剩余过期时间
        
        Args:
            namespace: 命名空间
            key: 键
        
        Returns:
            剩余秒数，-1表示永不过期，-2表示不存在
        """
        if self.client is None:
            return -1 if self.exists(namespace, key) else -2
        
        cache_key = self._make_key(namespace, key)
        
        try:
            return self.client.ttl(cache_key)
        except Exception as e:
            logger.error(f"获取TTL失败 {cache_key}: {e}")
            return -2


def cached(
    namespace: str,
    ttl: int = 300,
    key_func: Optional[Callable] = None
):
    """
    缓存装饰器
    
    Args:
        namespace: 命名空间
        ttl: 过期时间（秒）
        key_func: 生成缓存键的函数
    
    Example:
        @cached(namespace="orders", ttl=60)
        def get_orders(store_id, marketplace_id):
            # 函数实现
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(
                    ":".join(key_parts).encode()
                ).hexdigest()
            
            # 尝试从缓存获取
            cache = getattr(wrapper, '_cache', None)
            if cache:
                cached_value = cache.get(namespace, cache_key)
                if cached_value is not None:
                    logger.debug(f"从缓存获取: {namespace}:{cache_key}")
                    return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if cache and result is not None:
                cache.set(namespace, cache_key, result, ttl)
                logger.debug(f"存入缓存: {namespace}:{cache_key}")
            
            return result
        
        return wrapper
    return decorator


# 全局缓存实例
_global_cache: Optional[RedisCache] = None


def init_cache(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None
) -> RedisCache:
    """
    初始化全局缓存实例
    
    Args:
        host: Redis主机
        port: Redis端口
        db: 数据库编号
        password: 密码
    
    Returns:
        缓存实例
    """
    global _global_cache
    _global_cache = RedisCache(host, port, db, password)
    return _global_cache


def get_cache() -> Optional[RedisCache]:
    """获取全局缓存实例"""
    return _global_cache


if __name__ == "__main__":
    # 测试
    cache = RedisCache()
    cache.set("test", "key1", {"data": "value"}, ttl=60)
    print(cache.get("test", "key1"))