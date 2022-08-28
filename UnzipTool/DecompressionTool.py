# -*- coding: utf-8 -*-

"""
@Author  : LIAN
@Project : ToolComponents
@File    : DecompressionTool.py
@Time    : 2022/03/03
@License : (C) Copyright 2022, RoarPanda Corporation.
"""

"""
解压模块，支持多种解压方法（tar,gz,xz,bz2,zip,rar,7z），支持多级解压
前提添加： sudo apt-get install unar / python3.5 rarfile 3.0 
"""

import datetime
import zipfile
import subprocess
import rarfile
import hashlib
import os
import magic


class My7z(object):
    file_path = None
    uncompress_password = None

    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            raise FileNotFoundError

    def setpassword(self, uncompress_password=None):
        self.uncompress_password = uncompress_password

    def extractall(self, path=None):
        if path is None:
            path = "CompressFile"
        # uncompress_command = "7z x -o{} -p{} {}".format(path, self.uncompress_password, self.file_path)
        if self.uncompress_password is None or self.uncompress_password == "":
            uncompress_command = "unar -f {} -o {}".format(self.file_path, path)
        else:
            self.uncompress_password = str(self.uncompress_password)
            uncompress_command = "unar -f -p {} {} -o {}".format(self.uncompress_password, self.file_path, path)
        p = subprocess.Popen(uncompress_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(p.stdout.read())
        print(p.stderr.read())
        p.communicate()
        print("uncompress status code: ")
        print(p.returncode)
        return p.returncode
        # if p.returncode != 0:
        #     raise Exception("password wrong")


class TarArchive(object):
    file_path = None

    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            raise FileNotFoundError

    def extractall(self, path=None):
        if path is None:
            path = "CompressFile"
        p = subprocess.Popen("tar -xf {} -C {}".format(self.file_path, path),
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.communicate()
        if p.returncode != 0:
            raise Exception("Extract Error")


# 为文件分配对应的解压缩对象
class UncompressDispatch(object):
    uncompress_obj = None

    def __init__(self, file_path=None, file_type=None, uncompress_password=None):
        self.fileType = file_type
        self.filePath = file_path
        self.uncompressPassword = uncompress_password
        self.init_uncompress_obj(file_path)

    def init_uncompress_obj(self, file_path):
        if "zip" == self.fileType.split("/")[-1].strip():
            try:
                self.uncompress_obj = zipfile.ZipFile(file_path)
            except Exception:
                self.fileType = "Unrecognized file type"
                return
            if "AndroidManifest.xml" in self.uncompress_obj.namelist():
                self.fileType = "APK file, Android"
                return
            elif "[Content_Types].xml" in self.uncompress_obj.namelist():
                self.fileType = "Microsoft Office file"
                return
            # Use 7z uncompress method to deal
            self.uncompress_obj = My7z(file_path)
            if self.uncompressPassword is not None:
                self.uncompress_obj.setpassword(self.uncompressPassword)

        elif self.fileType.split("/")[-1].strip() in ["x-tar", "gzip", "x-xz", "x-bzip2"]:
            # self.uncompress_obj = TarArchive(file_path)
            self.uncompress_obj = My7z(file_path)

        elif "rar" in self.fileType:
            # self.uncompress_obj = rarfile.RarFile(file_path)
            # if self.uncompressPassword is not None:
            # self.uncompress_obj.extractall(path= ,pwd=self.uncompressPassword)
            self.uncompress_obj = My7z(file_path)
            if self.uncompressPassword is not None:
                self.uncompress_obj.setpassword(self.uncompressPassword)

        elif "7z" in self.fileType:
            self.uncompress_obj = My7z(file_path)
            if self.uncompressPassword is not None:
                self.uncompress_obj.setpassword(self.uncompressPassword)

        else:
            pass

    def extract(self, path=None):
        if "zip" == self.fileType.split("/")[-1].strip():
            return self.uncompress_obj.extractall(path=path)
        elif self.fileType.split("/")[-1].strip() in ["x-tar", "gzip", "x-xz", "x-bzip2"]:
            return self.uncompress_obj.extractall(path=path)
        elif "rar" in self.fileType:
            return self.uncompress_obj.extractall(path=path)
        elif "7z" in self.fileType:
            return self.uncompress_obj.extractall(path=path)
        else:
            pass

    def rar_extract(self, path=None, extract_dir=None):
        rar = rarfile.RarFile(path)
        if self.uncompressPassword is not None:
            rep = rar.extractall(path=extract_dir, pwd=self.uncompressPassword)
        else:
            rep = rar.extractall(path=extract_dir)
        return rep


class UncompressMod(object):
    fileMD5 = None
    zipObj = None
    uncompressObj = None

    def __init__(self, file_path=None, uncompress_password=None):

        if os.path.exists(file_path):
            self.filePath = file_path
            self.fileType = self.file_distinguish()
            self.uncompress_password = uncompress_password
            self.uncompressObj = UncompressDispatch(self.filePath,
                                                    self.fileType,
                                                    self.uncompress_password)
            with open(file_path, "rb") as fp:
                md5 = hashlib.md5()
                md5.update(fp.read())
                self.fileMD5 = md5.hexdigest()
            fp.close()

    def file_distinguish(self):
        magic_obj = magic.Magic(mime=True)
        with open(self.filePath, "rb") as f:
            msg = magic_obj.from_buffer(f.read())
        del magic_obj
        return msg

    def extract_file(self, extract_path=None):

        if self.uncompressObj.uncompress_obj is None:
            return None, 1

        if extract_path is None:
            _, file_name = os.path.split(self.filePath)
            extract_path, _ = os.path.splitext(file_name)

        tmp_extract_path = extract_path
        if not os.path.exists(tmp_extract_path):
            os.mkdir(tmp_extract_path)

        try:
            if "rar" in self.fileType:
                uncom_code = self.uncompressObj.rar_extract(path=self.filePath, extract_dir=tmp_extract_path)
                if uncom_code is None:
                    return tmp_extract_path, 0
                else:
                    return uncom_code
            else:
                uncom_code = self.uncompressObj.extract(tmp_extract_path)
            if uncom_code != 0:
                return None, uncom_code
            else:
                return tmp_extract_path, 0
        except Exception as e:
            print(str(e))
            if 'The specified password is incorrect' in str(e) and self.uncompress_password is not None:
                # Password Error
                return None, 1
            # Need Password
            return None, 2


class RecursionUncompress(object):
    """
    Main Uncompress Process
    """

    @staticmethod
    def extract_with_level(file_path, extract_level, uncompress_password=None, extract_dir="tmp_{}_{}"):
        """
        按“extract_level”等级的解压力度解压路径在“file_path”下的文件
        :param file_path: 要解压文件的路径
        :param extract_level: 解压等级
        :param uncompress_password: 解压密码 Bytes
        :return:
        (解压到的主文件夹，解压完成的文件集合)
        """
        compress_file_queue_list = list()
        detect_sample_set = set()
        # Init compressed file list
        compress_file_queue_list.append(file_path)
        is_first = 1
        first_dir = ""
        # Use Queue to deal with breadth-first traversal
        while len(compress_file_queue_list) != 0:
            if extract_level == 0:
                break
            if is_first == 1:
                with open(file_path, "rb") as fp:
                    file_md5 = hashlib.md5(fp.read()).hexdigest()
                fp.close()
                now_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")
                base_extract_path = extract_dir.format(now_time, file_md5)
                first_dir = base_extract_path
            else:
                base_extract_path, _ = os.path.split(compress_file_queue_list[-1])
            # Extract compressed file
            extract_file_path = compress_file_queue_list.pop()
            tmp_object = UncompressMod(file_path=extract_file_path, uncompress_password=uncompress_password)
            if None in [tmp_object.filePath, tmp_object.uncompressObj]:
                continue
            tmp_extract_path, e_flag = tmp_object.extract_file(base_extract_path)
            del tmp_object

            # Can't Extract perhaps have password
            if tmp_extract_path is None:
                # Return Root file
                if is_first == 1:
                    if e_flag == 2:
                        return first_dir, 2
                detect_sample_set.add(extract_file_path)
                continue

            # Remove compressed file (do not delete the root file)
            if is_first == 0:
                os.remove(extract_file_path)
            else:
                is_first = 0

            # Record compressed files into queue
            for base_dir, _, files in os.walk(tmp_extract_path):
                for f in files:
                    file_abspath = os.path.join(base_dir, f)
                    tmp_object = UncompressMod(file_abspath)
                    if tmp_object.uncompressObj is None:
                        detect_sample_set.add(file_abspath)
                        del tmp_object
                        continue
                    if tmp_object.uncompressObj.uncompress_obj is not None:
                        compress_file_queue_list.append(file_abspath)
                        if file_abspath != extract_file_path:
                            detect_sample_set.add(file_abspath)
                    else:
                        # Record simple files into detect list
                        detect_sample_set.add(file_abspath)
                    del tmp_object
            extract_level -= 1
        return first_dir, detect_sample_set


class CompressedHandler(object):
    """
    功能：压缩文件的解压
    流程：1. 校验是否是压缩文件 2. 提取子文件  3. 提取成功，父文件子文件推进检测并入库 4. 提取失败，压缩文件入库
    """

    def __init__(self, file_path=None, unzip_path=None, extract_level=1, uncompress_password=None, recheck=0):
        """
        :param file_path: 解压文件路径
        :param unzip_path: 解压路径
        :param extract_level: 解压等级
        :param uncompress_password: 解压密码
        :param recheck: 是否要对已经检测过的解压缩文件重新进行检测
        :return 0 正常 -1 异常 2 需要密码
        """
        self.file_path = file_path
        self.extract_level = extract_level
        self.uncompress_password = uncompress_password
        self.recheck = recheck
        self.uncompress_obj = RecursionUncompress
        self.unzip_path = unzip_path

    def compressed_handler(self):

        # 进行解包操作
        extract = self.compressed_extract()
        if extract == -1:
            print("compressed file extract fail !!!")
            return -1

        if extract == 2:
            # 保存主文件 需要密码
            return 2

        return extract

    def compressed_extract(self):
        # 解压文件，获取解压文件的根目录和其子文件路径
        try:
            # extract_path 解压文件路径  sample_file_set 子文件
            extract_path, sample_file_set = self.uncompress_obj.extract_with_level(file_path=self.file_path,
                                                                                   extract_level=self.extract_level,
                                                                                   uncompress_password=self.uncompress_password,
                                                                                   extract_dir=self.unzip_path)
        except Exception as e:
            print(str(e))
            return -1

        if type(sample_file_set) is int:
            print("Need Password")
            return 2

        return extract_path, sample_file_set


if __name__ == '__main__':
    # 使用示例
    # file_path: 解压文件路径
    # unzip_path: 解压路径
    # extract_level: 解压等级
    # uncompress_password: 解压密码
    # recheck: 是否要对已经检测过的解压缩文件重新进行检测
    # return -1----解压失败 2--需要密码 其它-- extract_path 解压文件路径  sample_file_set 子文件
    file_path = "/home/rpadmin/test/testmim4.rar"
    unzip_path = "/home/rpadmin/test/"
    extract_level = 1
    uncompress_password = "123456"

    compressed_result = CompressedHandler(file_path=file_path, unzip_path=unzip_path, extract_level=extract_level,
                                          uncompress_password=uncompress_password, recheck=0).compressed_handler()
    print("compressed_result:::::", compressed_result)
