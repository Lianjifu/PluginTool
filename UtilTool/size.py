# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : UtilTool
@File    : size.py
@Time    : 2022/03/07
@License : (C) Copyright 2022, RoarPanda Corporation.
"""


# 格式化size 字节转相应的单位
def format_size(size_bytes):
    """format size"""
    try:
        if not size_bytes:
            size_bytes = 0
        size_bytes = float(size_bytes)
        size_kb = float(size_bytes / 1024)
    except Exception as e:
        print(str(e))
        return 0

    if size_kb >= 1024:
        size_mb = float(size_kb / 1024)
        if size_mb >= 1024:
            size_gb = float(size_mb / 1024)
            return "%0.1fG" % (size_gb)
        else:
            return "%0.1fM" % (size_mb)
    else:
        return "%0.1fK" % (size_kb)


# size 转换
def size_transition(sample_size):
    # 转换为字节
    if sample_size.endswith("B"):
        size = float(sample_size.split("B")[0])
    elif sample_size.endswith("K"):
        size = int(float(sample_size.split("K")[0]) * 1024)
    elif sample_size.endswith("M"):
        size = int(float(sample_size.split("M")[0]) * 1024 * 1024)
    elif sample_size.endswith("G"):
        size = int(float(sample_size.split("G")[0]) * 1024 * 1024 * 1024)
    elif sample_size.endswith("T"):
        size = int(float(sample_size.split("T")[0]) * 1024 * 1024 * 1024 * 1024)
    else:
        size = int(config.sample_size)

    return size


if __name__ == '__main__':
    # 字节格式化成带单位
    size_bytes = "12231234234"
    size = format_size(size_bytes)

    # 带单位转换为字节
    sample_size = "23M"
    size_byte = size_transition(sample_size)
