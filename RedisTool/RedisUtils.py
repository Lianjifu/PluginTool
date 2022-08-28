# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : RedisTool
@File    : RedisUtils.py
@Time    : 2022/03/07
@License : (C) Copyright 2022, RoarPanda Corporation.
"""

import redis
import threading


class RedisConf:
    """Redis config info"""

    def __init__(self, env="local", db=1):
        self.env = env
        self.db = db

    @property
    def env_options(self):
        if self.env == "prod":
            redis_config = {
                "host": "",
                "port": 6379,
                "password": "",
                "db": self.db,
                "encoding": "utf-8",
                "decode_responses": True,  # decode python unicode
                "target_max_memory": 3896,
                "max_connections": 1
            }

        elif self.env == "test":
            redis_config = {
                "host": "",
                "port": 6379,
                "password": "",
                "db": self.db,
                "encoding": "utf-8",
                "decode_responses": True,  # decode python unicode
                "target_max_memory": 3896,
                "max_connections": 1
            }
        else:
            redis_config = {
                "host": "127.0.0.1",
                "port": 6379,
                "password": "",
                "db": self.db,
                "encoding": "utf-8",
                "decode_responses": True,  # decode python unicode
                "target_max_memory": 3896,
                "max_connections": 1
            }
        return redis_config


class RedisUntil(object):
    """Redis operating mode"""

    def __init__(self):
        """Redis connection info"""
        self.config = RedisConf().env_options
        self.connection_client = None
        self.connection_pool = None
        # self.mutex = threading.Lock()

        max_conn = 1
        if "max_connections" in self.config:
            max_conn = self.config["max_connections"]
            if max_conn <= 0:
                max_conn = 1
        decode_responses = False
        if "decode_responses" in self.config:
            decode_responses = self.config["decode_responses"]
        self.connection_pool = redis.ConnectionPool(host=self.config['host'], port=self.config['port'],
                                                    db=self.config['db'], password=self.config['password'],
                                                    encoding=self.config['encoding'], max_connections=max_conn,
                                                    decode_responses=decode_responses)
        self.connection_client = redis.Redis(connection_pool=self.connection_pool)

    def close(self):
        if self.connection_pool:
            self.connection_pool.disconnect()

    def rpush(self, key, json_text, expired_in_seconds=0):
        r = self.connection_client
        # self.mutex.acquire()
        pipe = r.pipeline()
        pipe.rpush(key, json_text)
        if expired_in_seconds > 0:
            pipe.expire(key, expired_in_seconds)
        pipe.execute()
        # self.mutex.release()

    def lpush(self, key, json_text, expired_in_seconds=0):
        r = self.connection_client
        # self.mutex.acquire()
        pipe = r.pipeline()
        pipe.lpush(key, json_text)
        if expired_in_seconds > 0:
            pipe.expire(key, expired_in_seconds)
        pipe.execute()
        # self.mutex.release()

    def lpop_pipline(self, key, length):
        i = 0
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        curent_len = r.llen(key)
        if curent_len > 0:
            target_len = 0
            if curent_len > length:
                target_len = length
            else:
                target_len = curent_len
            pipe = r.pipeline()
            while i < target_len:
                pipe.lpop(key)
                i += 1
            temp_poped_items = pipe.execute()
            poped_items = temp_poped_items
        # self.mutex.release()
        return poped_items

    def lpop(self, key):
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        data = r.lpop(key)
        if data:
            poped_items.append(data)
        # self.mutex.release()
        return poped_items

    def rpop_pipline(self, key, length):
        i = 0
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        curent_len = r.llen(key)
        if curent_len > 0:
            target_len = 0
            if curent_len > length:
                target_len = length
            else:
                target_len = curent_len
            pipe = r.pipeline()
            while i < target_len:
                pipe.rpop(key)
                i += 1
            temp_poped_items = pipe.execute()
            poped_items = temp_poped_items
        # self.mutex.release()
        return poped_items

    def rpop(self, key):
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        data = r.rpop(key)
        if data:
            poped_items.append(data)
        # self.mutex.release()
        return poped_items

    def hincrby(self, hash_key, field, amount=1):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hincrby(hash_key, field, amount)
        # self.mutex.release()
        return result

    def llen(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.llen(key)
        # self.mutex.release()
        return result

    def hdel(self, key, field):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hdel(key, field)
        # self.mutex.release()
        return result

    def hset(self, key, field, value, expired_in_seconds=0):
        r = self.connection_client
        # self.mutex.acquire()
        pipline = r.pipeline()
        pipline.hset(key, field, value)
        if expired_in_seconds > 0:
            pipline.expire(key, expired_in_seconds)
        pipline.execute()
        # self.mutex.release()

    def info(self, section=None):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.info(section)
        # self.mutex.release()
        return result

    def exceed_memory_limits(self):
        result = False
        if "target_max_memory" in self.config.keys():
            target_max_memory = self.config["target_max_memory"]
            redis_info = self.info("memory")
            distance = self.__max_memory_distance(redis_info, target_max_memory)
            if distance and distance <= 0:
                result = True
        return result

    def __max_memory_distance(self, redis_info_dict, target_max):
        # # Memory
        # used_memory:472978192
        # used_memory_human:451.07M
        # used_memory_rss:510640128
        # used_memory_peak:493548568
        # used_memory_peak_human:470.68M
        # used_memory_lua:35840
        # mem_fragmentation_ratio:1.08
        # mem_allocator:jemalloc - 3.6.0
        result = None
        if "used_memory" in redis_info_dict.keys():
            temp_used = int(redis_info_dict["used_memory"])
            temp_used = temp_used / (1024 * 1024)
            result = target_max - temp_used
        else:
            print("used_memory is not found!")
        return result

    def sadd(self, key, value):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.sadd(key, value)
        # self.mutex.release()
        return result

    def sismember(self, key, value):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.sismember(key, value)
        # self.mutex.release()
        return result

    def exists(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.exists(key)
        # self.mutex.release()
        return result

    def keys(self, pattern):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.keys(pattern=pattern)
        # self.mutex.release()
        return result

    def get(self, name):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.get(name=name)
        # self.mutex.release()
        return result

    def delele(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        r.delete(key)
        # self.mutex.release()

    def scan(self, cursor, match=None, count=50):
        """
        :param cursor:
        :param match:
        :param count:
        :return:
         (new_cursor,
            [key1, key2, key3 ...])
        """
        r = self.connection_client
        # self.mutex.acquire()
        result = r.scan(cursor=cursor, match=match, count=count)
        # self.mutex.release()
        return result

    def hmget(self, hash_key, fields_list):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hmget(hash_key, fields_list)
        # self.mutex.release()
        return result

    def set(self, key, value, ex=None):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.set(key, value, ex)
        # self.mutex.release()
        return result


if __name__ == '__main__':
    mc = RedisUntil()
    # print(mc)
