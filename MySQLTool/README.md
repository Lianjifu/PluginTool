## MySQLTool

##### 1. 工具说明

> mysql 基础使用的封装，可进行单次连接使用，也可以使用连接池进行使用

- 使用用例

```python
# 使用普通连接 不需要传isPool=False
def domeTest(self, sample_md5):
    time_list = []
    DbInit = MysqlUtil()
    try:
        select_sql = """select create_time from sampleDetect_sampleinfo where sample_md5=%s;"""
        DbRsSel = DbInit.select_sql(select_sql, sample_md5, _type=0)
        if DbRsSel:
            for row in DbRsSel:
                m = {
                    "create_time": row["create_time"]
                }
                time_list.append(m)
    except Exception as e:
        self.log_sql.error("select sample_md5 error::", str(e))
    DbInit.close()
    return time_list

```

##### 2. 环境说明

- pip install DBUtils
- pip install pymysql
