"""缓存模块"""
from .redis_cache import RedisCache, init_cache, get_cache, cached

__all__ = ['RedisCache', 'init_cache', 'get_cache', 'cached']