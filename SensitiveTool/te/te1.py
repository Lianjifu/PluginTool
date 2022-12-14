# -*- coding:utf-8 -*-

# DFA算法
class DFAFilter(object):
    def __init__(self):
        self.keyword_chains = {}  # 关键词链表
        self.delimit = '\x00'  # 限定

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
        with open(path, encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())
        # print(self.keyword_chains)

    def filter(self, message, repl="*"):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)


def readtxt(path):
    gfw = DFAFilter()
    path2 = "1.txt"
    gfw.parse(path2)
    try:
        with open(path) as f:
            path_info = f.readline()
            print("path_info::", path_info)
            # print("path_info",path_info)
            result = gfw.filter(path_info)
            # print(result)
    except Exception as e:
        print("e:::::::::::", e)
        raise e

    # with open(path) as f:
    #     path_info = f.readline()
    #     print("path_info::",path_info)
    #     # print("path_info",path_info)
    #     result = gfw.filter(path_info)
    #     print(result)

### 蚂蚁
if __name__ == "__main__":
    # text = "你真是个大傻逼，大傻子，傻大个，大坏蛋，坏人。"
    # text1 = "The eyes of some fish have a greater sensitivity to light than ours do."
    path1 = "2.pdf"
    path_info = readtxt(path1)

    # print(text)
