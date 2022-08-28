# -*- coding:utf-8 -*-
"""
需求： 对不同的文档进行处理。并根据关键词进行匹配
输出： 是否包含关键词语的文件名称
step1： 文件处理
step2:  敏感词处理
step3:  模式匹配

# configparser
配置模块
pip install configparser

# magic
文件类型模块
pip install python-magic

# subprocess 模块是doc文档使用方式
注意： linux 下需要安装antiword 
sudo apt install antiword 
使用： antiword test.doc 测试安装是否成功

# docx 
# 处理docx文件
需要安装python-docx
pip install python-docx


# pdfplumber 支持python3.6以上版本
# 处理pdf模块

# email  
pip install HTMLParser
# 处理邮箱模块

# chardet
pip install chardet
# 处理txt文档编码

# 记录 wps 的docx 无法识别 只能通过后缀来识别
"""
import chardet
import magic
import subprocess
import docx
import pdfplumber
import os
import email
from html.parser import HTMLParser
import configparser


class KeywordChains(object):
    """关键字处理"""

    def __init__(self):
        self.keyword_chains = {}  # 关键词链表
        self.delimit = '\x00'  # 限定
        self.config = configparser.ConfigParser()

    def add(self, keyword):
        keyword = keyword.lower()  # 关键词英文变为小写
        chars = keyword.strip()  # 关键字去除首尾空格和换行
        if not chars:  # 如果关键词为空直接返回
            return
        level = self.keyword_chains
        # 遍历关键字的每个字
        for i in range(len(chars)):
            # 如果这个字已经存在字符链的key中就进入其子字典
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        grouplist = self.get_keyword(path)
        if grouplist is False:
            return False

        chains_list = []
        for group in grouplist:
            group_name = group["group_name"]
            keyword_list = group["keyword_list"]
            for keyword in group["keyword_list"]:
                self.add(str(keyword).strip())
                n = {"group_name": group_name, "keyword": keyword, "keyword_chains": self.keyword_chains}
                chains_list.append(n)
                self.keyword_chains = {}
        return chains_list

    def get_keyword(self, path):
        grouplist = []
        self.config.read(path)
        sections = self.config.sections()

        for section in sections:
            if self.config.has_section(section):
                keylist = [keyword for k in self.config[section] for keyword in eval(self.config[section][k])]
                m = {"group_name": section, "keyword_list": keylist}
                grouplist.append(m)

            else:
                return False

        return grouplist


class KeywordFileter(object):
    def __init__(self):
        self.delimit = '\x00'  # 限定

    def filter(self, message, keyword_chains):
        message = message.lower()
        start = 0
        count = 0
        while start < len(message):
            level = keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        count += 1
                        start += step_ins - 1
                        break
                else:
                    break
            start += 1
        print("count:::", count)
        return count


class FileSensitiveHandle(object):
    """文件类型处理"""

    def __init__(self, file_path, keyword_path):
        self.file_path = file_path
        self.keyword_path = keyword_path

    def file_type(self):
        """获取文件类型"""
        try:
            m = magic.Magic()
            res = m.from_file(self.file_path)
        except Exception as e:
            print("[:::file_type:::]Error::::::", str(e))
            return None
        return res

    def file_handle(self):
        """根据文件格式选择不同的方式打开"""
        ms_doc_word = "MICROSOFT OFFICE WORD"
        wps_doc_word = "WPS OFFICE"
        ms_docx_word = "MICROSOFT WORD"
        pdf_word = "PDF"
        txt_word = "UNICODE TEXT"
        eml_word = "MAIL"
        python_word = "PYTHON"
        html_word = "HTML DOCUMENT"
        xml_word = "XML"
        script_word = "SCRIPT"
        res = False
        KC = KeywordChains()
        chains_list = KC.parse(self.keyword_path)

        # 读取文件类型
        file_res = self.file_type()
        # file_path = self.file_path
        if file_res is None:
            return False

        # 获取文件名称
        filepath, tmpfiename = os.path.split(self.file_path)
        shotname, extension = os.path.splitext(tmpfiename)

        # 获取文件大小
        fsize = os.path.getsize(self.file_path)
        fsize = int(fsize / float(1024 * 1024))

        if fsize > 6 :
            res = self.txt_handle(chains_list)
            if res is False:
                return "文档处理失败"
        else:
            # 根据文件格式判断使用哪种方式打开
            if ms_doc_word in file_res.upper() or wps_doc_word in file_res.upper() or extension in '.doc':
                res = self.doc_handle(chains_list)
                if res is False:
                    return "文档处理失败"

            elif ms_docx_word in file_res.upper() or extension in '.docx':
                res = self.docx_handle(chains_list)
                if res is False:
                    return "文档处理失败"

            elif pdf_word in file_res.upper() or extension in '.pdf':
                # res = self.pdf_handle(chains_list)
                # if res is False:
                #     return "文档处理失败"
                pass

            elif python_word in file_res.upper() or txt_word in file_res.upper() or html_word in file_res.upper()\
                    or xml_word in file_res.upper() or script_word in file_res.upper() or extension in \
                    (".txt", ".py", ".xml", ".html", ".htm", ".js"):
                res = self.txt_handle(chains_list)
                if res is False:
                    return "文档处理失败"

            elif eml_word in file_res.upper() or extension in ".eml":
                res = self.eml_handle(chains_list)
                if res is False:
                    return "文档处理失败"

            else:
                print("不符合设定文件格式")
                return False
        return res

    def doc_handle(self, chains_list):
        """doc 文档处理"""
        res_list = []
        try:
            file_path = self.file_path
            KF = KeywordFileter()
            output = subprocess.check_output(['antiword', file_path])
            data = output.decode("utf-8")
            for chains in chains_list:
                group_name = chains["group_name"]
                keyword = chains["keyword"]
                keyword_chains = chains["keyword_chains"]
                res = KF.filter(data, keyword_chains)
                m = {"group_name": group_name, "keywords": {keyword: res}}
                res_list.append(m)
        except Exception as e:
            print("doc文件读取异常:::", str(e))
            res_list = False

        return res_list

    def docx_handle(self, chains_list):
        """docx 文档处理"""
        res_list = []
        try:
            KF = KeywordFileter()
            file = docx.Document(self.file_path)
            for chains in chains_list:
                group_name = chains["group_name"]
                keyword = chains["keyword"]
                keyword_chains = chains["keyword_chains"]
                docx_data = []
                for para in file.paragraphs:
                    data = para.text
                    if data == "":
                        continue
                    docx_data.append(data)
                res = KF.filter(str(docx_data), keyword_chains)
                m = {"group_name": group_name, "keywords": {keyword: res}}
                res_list.append(m)

        except Exception as e:
            print("docx文件读取异常:::", str(e))
            res_list = False

        return res_list

    def pdf_handle(self, chains_list):
        """pdf 文档处理"""
        res_list = []
        try:
            KF = KeywordFileter()
            with pdfplumber.open(self.file_path) as pdf:
                for chains in chains_list:
                    group_name = chains["group_name"]
                    keyword = chains["keyword"]
                    keyword_chains = chains["keyword_chains"]
                    for page_number in range(len(pdf.pages)):
                        page = pdf.pages[page_number]
                        data = page.extract_text().decode("utf-8")
                        res = KF.filter(data, keyword_chains)
                        m = {"group_name": group_name, "keywords": {keyword: res}}
                        res_list.append(m)

        except Exception as e:
            print("pdf文件读取异常:::", str(e))
            res_list = False

        return res_list

    def txt_handle(self, chains_list):
        """文本格式处理，txt py eml"""
        res_list = []
        KF = KeywordFileter()
        file = open(self.file_path, "rb")
        try:
            data = file.read()
            char_info = chardet.detect(data)["encoding"]
            txt_data = data.decode(char_info)
            for chains in chains_list:
                group_name = chains["group_name"]
                keyword = chains["keyword"]
                keyword_chains = chains["keyword_chains"]
                res = KF.filter(str(txt_data), keyword_chains)
                m = {"group_name": group_name, "keywords": {keyword: res}}
                res_list.append(m)

            file.close()
        except Exception as e:
            file.close()
            print("txt 文件读取异常:::", str(e))
            res_list = False

        return res_list

    def eml_handle(self, chains_list):
        """邮件处理"""
        res_list = []

        try:
            KF = KeywordFileter()
            with open(self.file_path) as f:
                for chains in chains_list:
                    group_name = chains["group_name"]
                    keyword = chains["keyword"]
                    keyword_chains = chains["keyword_chains"]
                    eml_data = []
                    msg = email.message_from_file(f)
                    for par in msg.walk():
                        html_data = par.get_payload()
                        data = HTMLParser().unescape(html_data)
                        eml_data.append(data)
                    res = KF.filter(str(eml_data), keyword_chains)
                    m = {"group_name": group_name, "keywords": {keyword: res}}
                    res_list.append(m)

        except Exception as e:
            print("eml文件读取异常:::", str(e))
            res_list = False
        return res_list


if __name__ == '__main__':
    # 关键词文件路径
    keyword_path = "./keywords.ini"
    # 检测的文档路径
    file_paths = [
        "xt1.pdf",
        "xt2.docx",
        "xt3.doc",
        "xt4.txt",
        "xt5.txt"
    ]
    # 匹配关键词
    for pa in file_paths:
        FSH = FileSensitiveHandle(pa, keyword_path)
        res = FSH.file_handle()
        if res:
            print(pa, res)
