# -*- coding: utf8 -*-
__author__ = '54'

import sys
sys.path.append('forms')
import socket
import time
import threading
import select
from multiprocessing import Process,Queue
import os
from forms.server import *

def run0():
    print "none process !"

p = Process(target=run0)
p.start()

class Main_processor_old(QtGui.QMainWindow):
    #thread_stop_flag=False#业务处理线程停止信号
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent=None)
        self.ui=Ui_frm_server()
        self.ui.setupUi(self)
        self.password=None
        self.listen_sock=None
        self.thread_sock=None#负责socket通讯与业务处理的子线程
        self.server_stop_flag=False#服务停止信号
        self.running_flag=False
        #预留初始密码复制操作
        #self.password =
        print(os.getpid())

    def btn_run(self):
        print('1')
        #self.server_processor=Process(target=self.run0)
        #self.server_processor.start()

        print('2')
        self.running_flag=True

    def stop(self):
        if self.running_flag!=False:
            self.server_stop_flag=True
            self.listen_sock.close()
            self.listen_sock=None
        else:
            self.ui.tb_sock.append(time.asctime()+':  Server is not running !')

    def run(self):  #启动socket线程,开始监听端口
        print ('3')
        print(os.getpid())
        if self.password==None:
            self.ui.tb_sock.append(time.asctime()+':  please set password ! ')
        else:
            try:
                #配置socket
                self.listen_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.listen_sock.setblocking(1)#socket使用阻塞模式
                self.listen_sock.bind(('0.0.0.0',54254))
                self.listen_sock.listen(1) #只监听1个连接
                self.ui.tb_sock.append(time.asctime()+':  Server is running,waiting for connect...')
                list_socket=[self.listen_sock]
                while True: #监听socket连接的循环
                    if self.server_stop_flag==True:#循环开始时监测是否有关闭服务运行的信号,如果有,跳出循环
                        self.ui.tb_sock.append(time.asctime()+':  Server is stopping...')
                        break
                    else:
                        re,ws,es=select.select(list_socket,[],[],5)
                        for r in re:
                            if r is self.listen_sock:
                                sock,addr=listen_sock.accept()
                                #建立新线程用于处理TCP连接(二期改造为多center连接时的多线程施工点)
                                self.thread_sock=threading.current_thread(target=link_processor,args=(sock,addr))
                                self.thread_sock.start()
                            else:
                                data=r.recv(1024)
                                if not data:
                                    continue
                self.ui.tb_sock.append(time.asctime()+':  Server is stopped')
            except socket.error,e:
                self.ui.tb_sock.append(time.asctime()+':  socket error '+e)
            finally:
                self.listen_sock.close()
    #连接处理函数
    def link_processor(self,sock,addr):
        self.ui.tb_sock.append(time.asctime()+':  Accept new center connection form '+addr)
        #进入密码验证循环
        try:
            while True: #密码验证处理外层循环
                while True:#循环recv()循环
                    recv_data=sock.recv(4096)
                    if len(recv_data) !=0:
                        break
                #监测是否有关闭服务运行的信号,如果有,跳出循环
                if self.server_stop_flag==True:
                        self.ui.tb_sock.append(time.asctime()+':  Server is stopping...')
                        sock.sendall('exit')
                        break
                list=recv_data.split('♂')
                if list[0]=='login':
                    if list[1]==self.password:
                        sock.sendall('login♂success')
                        self.ui.tb_sock.append(time.asctime()+':  login success! welcome center from '+addr)
                        break
                    else:
                        sock.send('login♂wrong password')
                        self.ui.tb_sock.append(time.asctime()+':  wrong password,login fail from '+addr)
                        continue
                if list[0]=='exit':
                     self.ui.tb_sock.append(time.asctime()+':  exit received,link close '+addr)
                     break
            sock.close()
        #验证通过,进入命令处理循环,此处开始循环接收与处理命令
            while True:
                while True:#循环recv()循环
                    recv_data=sock.recv(4096)
                    if len(recv_data) !=0:break
                #监测是否有关闭服务运行的信号,如果有,跳出循环
                if self.server_stop_flag==True:
                        self.ui.tb_sock.append(time.asctime()+':  Server is in stopping...')
                        sock.sendall('exit')
                        break
                list=recv_data.split('♂')
                if list[0]=='exit':#判断是否为关闭连接的命令,如果是,跳出循环
                    self.ui.tb_sock.append(time.asctime()+':  [exit] received from'+addr)
                    break
                #传递拆分好的命令与参数list到vbox功能处理模块
                #vbox_funcation(list)
                self.ui.tb_sock.append(time.asctime()+':  [ '+recv_data+' ] is received from '+addr)
                #self.ui.tb_sock.append(time.asctime()+':  [ '+send_data+' ] is send to '+addr)
            sock.close()
        except socket.error,e:
            self.ui.tb_sock.append(time.asctime()+':  socket error '+e)
        finally:
            sock.close()

if __name__ == "__main__":
    app=QtGui.QApplication(sys.argv)
    myapp=Main_processor_old()
    myapp.show()
    sys.exit(app.exec_())
