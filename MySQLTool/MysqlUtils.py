# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : MySQLTool
@File    : MysqlUtils.py
@Time    : 2022/03/07
@License : (C) Copyright 2022, RoarPanda Corporation.
"""
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
# pip install DBUtils
# pip install pymysql

class MysqlConf:
    """Mysql config info"""

    def __init__(self, env="local"):
        self.env = env
        self.isPool = isPool

    @property
    def env_options(self):
        if self.env == "prod":
            db_conf = {
                "db_name": "",
                "db_host": "",
                "db_user": "",
                "db_password": "",
                "db_port": 3306,
                "db_charset": "utf8"
            }

        elif self.env == "test":
            db_conf = {
                "db_name": "",
                "db_host": "",
                "db_user": "",
                "db_password": "",
                "db_port": 3306,
                "db_charset": "utf8"
            }

        else:
            db_conf = {
                "db_name": "",
                "db_host": "",
                "db_user": "",
                "db_password": "",
                "db_port": 3306,
                "db_charset": "utf8"
            }

        return db_conf


class MysqlUtil(object):
    """Mysql operating mode"""

    def __init__(self, isPool=False):
        """Mysql connection info"""

        __pool = None
        
        if isPool:
            # 使用连接池包连接 
            self.conn = Mysql.__PoolConn()
            if self.conn:
                self.cur = self.conn.cursor()
            else:
                self.cur = None
        else:
            # 普通连接方式
            self.conn = self.__conn()
            if self.conn:
                self.cur = self.conn.cursor(DictCursor)
            else:
                self.cur = None

    def __conn(self):
        conn = None
        try:
            self.db_info = MysqlConf(env="local").env_options
            conn = pymysql.connect(host=self.db_info["db_host"], user=self.db_info["db_user"],
                                   password=self.db_info["db_password"], port=self.db_info["db_port"],
                                   database=self.db_info["db_name"], charset=self.db_info["db_charset"])
        except Exception as e:
            print("The mysql connection is abnormal ::::: ", str(e))
        return conn

    def __PoolConn(self):
        """
        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param passwd:密码
        :param charset:字符编码
        @return MySQLdb.connection
        """
        conn = None
        if MysqlUtil.__pool is None:
            try:
                self.db_info = MysqlConf(env="local").env_options
                __pool = PooledDB(creator=pymysql, mincached=1, maxcached=20,
                                  host=self.db_info["db_host"], port=self.db_info["db_port"],
                                  user=self.db_info["db_user"], passwd=self.db_info["db_password"],
                                  db=self.db_info["db_name"], use_unicode=False,
                                  charset=self.db_info["db_charset"], cursorclass=DictCursor)
                conn = __pool.connection()
            except Exception as e:
                print("The mysql connection is abnormal ::::: ", str(e))

        return conn

    def select_sql(self, _sql_str=None, _tuple=None, _type=0):
        """
        :param _sql_str: sql语句
        :param _tuple: 元组参数
        :param _type: 类型
        :return:
        """
        db_result = ()
        if _sql_str:
            try:
                if _type == 0:
                    if _tuple:
                        self.cur.execute(_sql_str, _tuple)
                        db_result = self.cur.fetchone()
                    else:
                        self.cur.execute(_sql_str)
                        db_result = self.cur.fetchone()
                else:
                    if _tuple:
                        self.cur.execute(_sql_str, _tuple)
                        db_result = self.cur.fetchall()
                    else:
                        self.cur.execute(_sql_str)
                        db_result = self.cur.fetchall()

            except Exception as e:
                print("selectSQL error ::::: ", str(e))
                db_result = ()
        else:
            pass
        return db_result

    def execute_sql(self, _sql_str=None, _tuple=None):
        """
        :param _sql_str: sql语句
        :param _tuple:  元组参数
        :return:
        """
        db_result = 0
        if _sql_str:
            try:
                if _tuple:
                    db_result = self.cur.execute(_sql_str, _tuple)
                else:
                    db_result = self.cur.execute(_sql_str)
            except Exception as e:
                print("executeSQL error ::::: ", str(e))
                db_result = 0

        else:
            pass
        return db_result

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    # isPool 默认为False 不启用连接池
    mc = MysqlUtil(isPool=False)
    print(mc)
