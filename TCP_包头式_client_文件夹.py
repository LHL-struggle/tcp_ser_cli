'''
文件描述信息结构为：文件名（300B,右边填充空格，utf-8编码）+文件大小（15B右边填充空格）
'''
from socket import *
import hashlib
import os
def md5(file_path):
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            m.update(data)
    return m.hexdigest().upper()       # 大写

# 创建客户端套接字
client_socket = socket(AF_INET, SOCK_STREAM)
# 绑定本机地址与固定端口号
client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
client_socket.bind(('0.0.0.0', 8888))
# 服务器的地址与端口号
'''
with open('C:\\Users\\Administrator\\Desktop\\Py_Home folder\\配置文件\\IP_address.txt', 'rb') as f:
    servers_address = tuple(eval(f.read().decode()))  # 字节型转换为字符串型,在将字符串型转换为元组型
'''
#print(servers_address)
# 服务器的地址与端口号
servers_address = ('192.168.8.183', 7777)
# servers_address = ('192.168.8.115', 9999)
# 连接到服务器
client_socket.connect(servers_address)
# 欲存放的文件路径
copy_path = 'C:\\Users\\Administrator\\Desktop\\a'
while 1:
    # 接收服务器返回的文件名称与大小,删除文件名右边的空白符，得取文件名
    file_path_name = client_socket.recv(300).decode().rstrip()
    if len(file_path_name) == 0:
        break
    #文件安放路径
    receive_file_path = copy_path + '\\' + file_path_name
    # 文件名
    file_name = file_path_name.split('\\')[-1]
    # 获取目录
    file_path = receive_file_path.replace(file_name, '')
    # 删除文件名大小值右边的空白符，得取文件大小
    file_size = int((client_socket.recv(15).decode()).rstrip())
    # 源文件的MD5值
    file_md5 = (client_socket.recv(32).decode()).rstrip()
    print('文件名：%s\n文件大小：%s\nmd5:%s' % (file_name, file_size, file_md5))

    # 如果file_size == -1则表示为空目录
    if file_size == -1:
        os.makedirs(receive_file_path)    # 创建空目录
        print('创建了空目录%s' % receive_file_path)
        continue    # 跳出此次循环

    # 判断路径是否存在,如果不存在则创建文件夹
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print('创建了:%s' % file_path)

    # 已拷贝文件大小
    copy_size = 0
    while 1:
        # 接收服务器返回的信息
        '''
        注意TCP并不是以包的形式发的，他是以字节流的形式发送的所以可能会出现粘包问题
        注意recv接收值为理想接收值但实际上却并不一定能够接收这么多，官方建议最多只能接收8k的数据
        解决办法：recv接收的文件大小设为：源文件大小 - 已拷贝文件大小，在循环接收，直到文件接收完毕，跳出循环接收
        '''
        receive_file = client_socket.recv(file_size - copy_size)
        if len(receive_file) == 0:
            # 如果是空文件，则创建一个空的文件
            open(receive_file_path, "ab").close()
            break
        # 已拷贝文件大小
        copy_size += len(receive_file)
        # 打开文件并想文件中写入拷贝的内容
        with open(receive_file_path, "ab") as f:
                f.write(receive_file)
        # 如果文件拷贝大小等于要拷贝的文件大小，则提示数据传输完成，跳出循环，
        if copy_size == file_size:
            break
    print('数据传输已完成：', copy_size)
    # 比对源文件的MD5值与拷贝文件的MD5值是否一致
    if md5(receive_file_path) == file_md5:
        print('%s拷贝文件与源文件一致\n' % file_name)
    else:
        print('%s拷贝文件与源文件不一致，拷贝失败' % file_name)
        break
# 关闭客户端套接字
client_socket.close()
