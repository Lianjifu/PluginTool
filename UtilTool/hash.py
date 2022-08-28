# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : UtilTool
@File    : hash.py
@Time    : 2022/03/07
@License : (C) Copyright 2022, RoarPanda Corporation.
"""
import hashlib


class HashHandler(object):
    """hash处理 默认为md5"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.f = open(self.file_path, "rb")

    def get_md5(self):
        data = self.f.read()
        m1 = hashlib.md5()
        m1.update(data)
        md5 = m1.hexdigest().upper()
        self.f.close()
        return md5

    def get_sha256(self):
        data = self.f.read()
        m1 = hashlib.sha256()
        m1.update(data)
        sha256 = m1.hexdigest().upper()
        self.f.close()
        return sha256

    def get_sha1(self):
        data = self.f.read()
        m1 = hashlib.sha1()
        m1.update(data)
        sha1 = m1.hexdigest().upper()
        self.f.close()
        return sha1


if __name__ == '__main__':
    file_path = "hash.py"
    file_md5 = HashHandler(file_path=file_path).get_md5()
    file_sha256 = HashHandler(file_path=file_path).get_sha256()
    file_sha1 = HashHandler(file_path=file_path).get_sha1()