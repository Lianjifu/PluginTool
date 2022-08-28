# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : UtilTool
@File    : ssh.py
@Time    : 2022/03/07
@License : (C) Copyright 2022, RoarPanda Corporation.
"""

import paramiko
# pip install paramiko


class SSHConnection(object):
    """
    ssh 连接并执行相应linux命令
    """
    def __init__(self, physical_host):
        self.host = physical_host['host']
        self.port = physical_host['port']
        self.username = physical_host['username']
        self.pwd = physical_host['pwd']
        self.connect = self.connect()

    def connect(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.pwd)
        self.__transport = transport

    def close(self):
        self.__transport.close()

    def run_cmd(self, command):
        """
         执行shell命令,返回字典
         return {'code': -1,'res':error}或
         return {'code': 0, 'res':res}
        :param command:
        :return:
        """
        ssh = paramiko.SSHClient()
        ssh._transport = self.__transport
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)
        # 获取命令结果
        res = self.to_str(stdout.read())
        # 获取错误信息
        error = self.to_str(stderr.read())
        # 如果有错误信息，返回error 否则返回res
        if "error" in error.lower():
            return {'code': -1, 'res': error}
        else:
            return {'code': 0, 'res': res}

    def to_str(self, bytes_or_str):
        """
        把byte类型转换为str
        :param bytes_or_str:
        :return:
        """
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')
        else:
            value = bytes_or_str
        return value

    # 销毁
    def __del__(self):
        self.close()


class SSHSftp(object):
    def __init__(self, physical_host):
        self.host = physical_host['host']
        self.port = physical_host['port']
        self.username = physical_host['username']
        self.pwd = physical_host['pwd']
        self.__client, self.__sftp = self.connect()

    def connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host, port=self.port, username=self.username, password=self.pwd)
        tran = client.get_transport()
        sftp = paramiko.SFTPClient.from_transport(tran)
        return client, sftp

    def close(self):
        self.__client.close()

    def sftp_cmd(self, remotepath):
        """
        :param remotepath: 文件目的路径
        :return: 文件路径
        """
        localpath = PathConfig.FilePath + remotepath.split('/')[-1]
        self.__sftp.get(remotepath, localpath=localpath)

        return localpath

    # 销毁
    def __del__(self):
        self.close()


if __name__ == '__main__':
    physical_host = {
        "host": "",
        "port": 22,
        "username": "",
        "pwd": "",
    }
    command = "cat ssh.py"
    # ssh shell 命令传输并执行
    comm_res = SSHConnection(physical_host).run_cmd(command)

    # ssh ftp 命令
    remote_path = "ssh.py"
    localpath = SSHSftp(physical_host).sftp_cmd(remote_path)
