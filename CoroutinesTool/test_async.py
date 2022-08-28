# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : CoroutinesTool
@File    : test.py
@Time    : 2022/03/03
@License : (C) Copyright 2022, RoarPanda Corporation.
"""

import asyncio
import time
from AsyncPoolHandler import AsyncPool


async def thread_example2(i):
    await asyncio.sleep(1)
    return i


async def thread_example3(i):
    time.sleep(1)
    await asyncio.sleep(0.1)
    return i


def thread_example4(i):
    time.sleep(4)
    return i


def my_callback(future):
    result = future.result()
    print('返回值: ', result)


def demo():
    # 任务组， 最大协程数
    pool = AsyncPool(maxsize=1000, pool_maxsize=900)

    # 插入任务任务
    for i in range(3000 + 1):
        # 非阻塞协程
        # pool.no_block_submit_args(thread_example2, i, callback=my_callback)
        # 阻塞协程
        pool.block_submit_args(thread_example4, i, callback=my_callback)

    print("等待子线程结束1...")

    # 停止子线程
    pool.release()

    print("等待子线程结束2...")

    # 等待
    # pool.wait()

    print("等待子线程结束3...")

    # 进度条使用
    while True:
        value = pool.task_progress(3000)
        print("value: ", value)

        # 获取线程数
        print("running: ", pool.running)

        if value == 100:
            break

        # 获取任务
        # print(pool.get_task())
        time.sleep(0.1)

    print("等待子线程结束4...")


if __name__ == '__main__':
    start_time = time.time()
    demo()
    end_time = time.time()
    print("run time: ", end_time - start_time)


