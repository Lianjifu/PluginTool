# -*- coding: utf-8 -*-
import magic
import docx
import os 
import email
import subprocess

from html.parser import HTMLParser
def file_type(file_path):
    try:
        m = magic.Magic()
        res = m.from_file(file_path)
    except Exception as e:
        print("[:::file_type:::]Error::::::", str(e))
        return None
    return res

def docx_handle(file_path):
    file = docx.Document(file_path)
    for para in file.paragraphs:
        data = para.text
        if data == "":
            continue
        print("data:::::",data)

def file_name(file_path):
    filepath, tmpfilename = os.path.split(file_path)
    shotname, extension = os.path.splitext(tmpfilename)
    print("filepath::::",filepath)
    print("shotname::::",shotname)
    print("extension:::",extension)


def txt_open(file_path):
    with open (file_path) as f:
        msg = email.message_from_file(f)
        #print("msg:::",msg)
        for par in msg.walk():
            data = par.get_payload()
            data = HTMLParser().unescape(data)
            print("data:::::",data)

def py_open(file_path):
    with open(file_path) as f:
        for line in f.readlines():
            print("data::::",line)

def doc_open(file_path):
    output = subprocess.check_output(['antiword',file_path])
    data = output.decode("utf-8")
    print("data:::",data)

if __name__ == '__main__':
    file_path = "/home/yuebao/test/sensitive/te/te1.doc"
    #res = file_type(file_path)
    #print("res:::::",res)
    #docx_handle(file_path)
    #file_name(file_path)
    #txt_open(file_path)
    #py_open(file_path)
    doc_open(file_path)

