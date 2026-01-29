import redis
from typing import Optional, Any

from app.config import settings


class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[str]:
        """获取Redis键值"""
        return self.redis_client.get(key)
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置Redis键值"""
        if expire:
            return self.redis_client.setex(key, expire, value)
        return self.redis_client.set(key, value)
    
    def delete(self, key: str) -> int:
        """删除Redis键"""
        return self.redis_client.delete(key)
    
    def exists(self, key: str) -> bool:
        """检查Redis键是否存在"""
        return bool(self.redis_client.exists(key))
    
    def incr(self, key: str) -> int:
        """自增Redis键值"""
        return self.redis_client.incr(key)
    
    def decr(self, key: str) -> int:
        """自减Redis键值"""
        return self.redis_client.decr(key)
    
    def lpush(self, key: str, *values) -> int:
        """左侧推入列表"""
        return self.redis_client.lpush(key, *values)
    
    def rpush(self, key: str, *values) -> int:
        """右侧推入列表"""
        return self.redis_client.rpush(key, *values)
    
    def lrange(self, key: str, start: int, end: int) -> list:
        """获取列表范围"""
        return self.redis_client.lrange(key, start, end)
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希表字段"""
        return self.redis_client.hget(name, key)
    
    def hset(self, name: str, key: str, value: Any) -> int:
        """设置哈希表字段"""
        return self.redis_client.hset(name, key, value)
    
    def hgetall(self, name: str) -> dict:
        """获取哈希表所有字段"""
        return self.redis_client.hgetall(name)
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        return self.redis_client.expire(key, seconds)
    
    def ttl(self, key: str) -> int:
        """获取键剩余过期时间"""
        return self.redis_client.ttl(key)


# 创建全局Redis客户端实例
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """获取Redis客户端的依赖函数"""
    return redis_client
