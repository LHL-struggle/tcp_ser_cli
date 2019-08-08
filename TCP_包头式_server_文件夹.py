#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import threading
import hashlib


def get_file_md5(file_path):
    m = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            m.update(data)

    return m.hexdigest().upper()


def send_one_file(sock_conn, file_abs_path):
    '''
    函数功能：将一个文件发送给客户端
    参数描述：
        sock_conn 套接字对象
        file_abs_path 待发送的文件的绝对路径
    '''
    file_name = file_abs_path[len(dest_file_parent_path):]
    if file_name[0] == '\\' or file_name[0] == '/':
        file_name = file_name[1:]

    file_size = os.path.getsize(file_abs_path)
    file_md5 = get_file_md5(file_abs_path)

    file_name = file_name.encode()
    file_name += b' ' * (200 - len(file_name))
    print(file_name.decode())
    file_size = "{:<15}".format(file_size).encode()
    print(file_size.decode())
    file_desc_info = file_name + file_size + file_md5.encode()

    sock_conn.send(file_desc_info)
    with open(file_abs_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            sock_conn.send(data)


def send_file_thread(sock_conn):
    try:
        for root, dirs, files in os.walk(dest_file_abs_path):
            for f in files:
                file_abs_path = os.path.join(root, f)
                print(file_abs_path)
                send_one_file(sock_conn, file_abs_path)
    except Exception as e:
        print(e)
    finally:
        sock_conn.close()


# dest_file_abs_path = 'C:\\Users\\Administrator\\Desktop\\music'
dest_file_abs_path = 'C:\\Users\\Administrator\\Desktop\\z'
# dest_file_abs_path = 'D:\python\文档\python代码'
print(dest_file_abs_path)
dest_file_parent_path = os.path.dirname(dest_file_abs_path)
dest_file_name = os.path.basename(dest_file_abs_path)

sock_listen = socket.socket()
sock_listen.bind(('192.168.8.183', 7777))
sock_listen.listen(5)

while True:
    sock_conn, client_addr = sock_listen.accept()
    print(client_addr, "已连接！")
    threading.Thread(target=send_file_thread, args=(sock_conn,)).start()

sock_listen.close()