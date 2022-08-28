##  SensitiveTool 使用

####  要求
- 需求： 对不同的文档进行处理。并根据关键词进行匹配
- 输出： 是否包含关键词语的文件名称

- step1： 文件处理
- step2:  敏感词处理
- step3:  模式匹配

#### 环境

- configparser 配置模块
> pip install configparser


- magic 模块
> pip install python-magic

 - subprocess 模块
> doc文档使用方式  
>  注意： linux 下需要安装antiword  
> 
>  sudo apt install antiword 
> 
>  antiword test.doc 测试安装是否成功

 - docx 模块 
> 需要安装python-docx
> 
> pip install python-docx

- pdfplumber 模块
> pdfplumber 支持python3.6以上版本

- email 模块
> 需要html 转码
> 
> pip install HTMLParser


- 记录 wps 的docx 无法识别 只能通过后缀来识别

#### 文件路径说明

 - 关键词文件路径 如dom.ini 所示,格式如下
```ini
[group1]

Keywords = ["蚂蚁", "蛐蛐", "蝴蝶"]

[group2]

Keywords = ["田园"]
```
 - 检测的文档路径
 - 输出格式：
```json
[
  {'group_name': 'group1', 'keywords': {'蚂蚁': 4}},
  {'group_name': 'group1', 'keywords': {'蛐蛐': 1}}, 
  {'group_name': 'group1', 'keywords': {'蝴蝶': 1}},
  {'group_name': 'group2', 'keywords': {'田园': 1}}
  ]
```